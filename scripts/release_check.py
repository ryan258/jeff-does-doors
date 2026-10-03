#!/usr/bin/env python3
"""Validate source policy and the exact generated artifact. No publication occurs."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
from content_policy import load_config, registry, enabled, frontmatter, page_feature, source_issues, required_sources, default_configs

ROOT = Path(__file__).resolve().parents[1]
CONFIG = None


def git_value(*args):
    """Return git output, or None when git fails (no repository, no commit)."""
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def feature_flags():
    config = CONFIG if CONFIG is not None else load_config(ROOT, 'hugo.toml')
    definitions = registry(ROOT)['features']
    flags = config.get('params', {}).get('features', {})
    return {name: enabled(name, flags, definitions) for name in definitions}


class PageAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.links: list[str] = []
        self.resources: list[str] = []
        self.missing_alt = 0
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.description_count = 0
        self.title_count = 0
        self.form_count = 0
        self.brief_form_count = 0
        self.in_title = False
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.structured_data: list[str] = []
        self.in_jsonld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if "id" in attributes and attributes["id"]:
            if attributes["id"] in self.ids: self.duplicate_ids.add(attributes["id"])
            self.ids.add(attributes["id"])
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self.in_jsonld = True
            self.structured_data.append("")
        if tag == "h1":
            self.h1_count += 1
        elif tag == "a" and attributes.get("href") is not None:
            self.links.append(attributes["href"] or "")
        elif tag == "img":
            if "alt" not in attributes:
                self.missing_alt += 1
            if attributes.get("src"):
                self.resources.append(attributes["src"] or "")
            for candidate in (attributes.get("srcset") or "").split(","):
                if candidate.strip(): self.resources.append(candidate.strip().split()[0])
        elif tag == "script" and attributes.get("src"):
            self.resources.append(attributes["src"] or "")
        elif tag == "link":
            href = attributes.get("href")
            if href:
                self.resources.append(href)
            rel = (attributes.get("rel") or "").lower().split()
            if "canonical" in rel and href:
                self.canonicals.append(href)
        elif tag == "meta":
            name = (attributes.get("name") or "").lower()
            if name == "description":
                self.description_count += 1
            elif name == "robots" and attributes.get("content"):
                self.robots.append((attributes.get("content") or "").lower())
        elif tag == "title":
            self.title_count += 1
            self.in_title = True
        elif tag == "form":
            self.form_count += 1
            if "data-project-form" in attributes:
                self.brief_form_count += 1

    def handle_data(self, data: str) -> None:
        if self.in_jsonld: self.structured_data[-1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script": self.in_jsonld = False
        if tag == "title":
            self.in_title = False


def normalized_base_url(raw: str) -> str | None:
    value = raw.strip()
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        return None
    hostname = (parsed.hostname or "").lower()
    if hostname in {"localhost", "127.0.0.1", "::1"}:
        return None
    if hostname.endswith((".example", ".invalid", ".test")):
        return None
    if "your-real-domain" in hostname or "example.com" in hostname:
        return None
    path = parsed.path or "/"
    if not path.startswith("/") or "//" in path:
        return None
    segments = path.split("/")
    if any(segment in {".", ".."} for segment in segments):
        return None
    normalized_path = "/" if path == "/" else f"/{path.strip('/')}/"
    return parsed._replace(path=normalized_path).geturl()


def path_relative_to_base(raw_path: str, base_url: str) -> str | None:
    """Return a built-output path, or None for a URL outside the site base path."""
    base_path = urlsplit(base_url).path.rstrip("/")
    path = unquote(raw_path or urlsplit(base_url).path or "/")
    if not path.startswith("/"):
        path = f"/{path}"
    if not base_path:
        return path
    if path == base_path:
        return "/"
    prefix = f"{base_path}/"
    if path.startswith(prefix):
        return path[len(base_path) :] or "/"
    return None


def output_path_for_url(build_dir: Path, raw_url: str, base_url: str, current_page: Path | None = None) -> Path | None:
    parsed = urlsplit(raw_url)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    base = urlsplit(base_url)
    if parsed.netloc and parsed.netloc != base.netloc:
        return None

    path_str = parsed.path
    if not path_str and parsed.fragment and current_page is not None:
        return current_page

    # Resolve document-relative links against current page's parent directory
    if not path_str.startswith("/") and current_page is not None:
        curr_rel = current_page.relative_to(build_dir)
        curr_dir = "/" if curr_rel.parent == Path(".") else f"/{curr_rel.parent.as_posix()}/"
        base_path = urlsplit(base_url).path.rstrip("/")
        full_virtual = posixpath.normpath(posixpath.join(base_path, curr_dir.lstrip("/"), path_str))
        if path_str.endswith("/"):
            full_virtual += "/"
        path_str = full_virtual

    path = path_relative_to_base(path_str, base_url)
    if path is None:
        return None
    if path == "/":
        return build_dir / "index.html"
    clean = path.lstrip("/")
    direct = build_dir / clean
    if direct.is_file():
        return direct
    if path.endswith("/"):
        return build_dir / clean / "index.html"
    return build_dir / f"{clean}.html"


def audit_build(build_dir: Path, base_url: str, staging: bool = False) -> list[str]:
    issues: list[str] = []
    features = feature_flags()
    for debris in build_dir.rglob(".DS_Store"):
        issues.append(f"Artifact contains OS debris: {debris.relative_to(build_dir)}")
    pages = sorted(build_dir.rglob("*.html"))
    if not pages:
        return ["Hugo produced no HTML pages"]

    # Pre-parse all pages to collect IDs for fragment verification
    parsed_pages: dict[Path, tuple[PageAudit, str]] = {}
    for page in pages:
        parser = PageAudit()
        text = page.read_text(encoding="utf-8")
        parser.feed(text)
        parsed_pages[page] = (parser, text)

    disabled_feature_paths = set()
    definitions = registry(ROOT)['features']
    for source in (ROOT / 'content').rglob('*.md'):
        data = frontmatter(source)
        flag = page_feature(source.relative_to(ROOT / 'content'), data, definitions)
        if (data.get("reviewOnly") and not staging) or (flag and not enabled(flag, features, definitions)):
            rel = source.relative_to(ROOT / 'content')
            route = rel.parent.as_posix() if rel.name == '_index.md' else rel.with_suffix('').as_posix()
            disabled_feature_paths.add('/' + route.strip('/') + '/index.html')

    for page, (parser, text) in parsed_pages.items():
        relative = page.relative_to(build_dir)
        label = "/" if relative == Path("index.html") else f"/{relative.as_posix()}"

        for duplicate in sorted(parser.duplicate_ids):
            issues.append(f"{label} has duplicate element ID: {duplicate}")
        for block in parser.structured_data:
            try:
                payload = json.loads(block)
                if not isinstance(payload, (dict, list)):
                    issues.append(f"{label} structured data must be an object or graph")
            except json.JSONDecodeError:
                issues.append(f"{label} has invalid JSON-LD")

        if parser.h1_count != 1:
            issues.append(f"{label} must contain exactly one h1 (found {parser.h1_count})")
        if parser.missing_alt:
            issues.append(f"{label} has {parser.missing_alt} image(s) without alt text")
        if parser.title_count != 1:
            issues.append(f"{label} must contain exactly one title element")
        if parser.description_count != 1:
            issues.append(f"{label} must contain exactly one meta description")

        if staging:
            if len(parser.robots) != 1 or "noindex" not in parser.robots[0] or "nofollow" not in parser.robots[0]:
                issues.append(f"{label} must contain exactly one noindex, nofollow robots directive in staging")
        else:
            # Check canonical matches expected specific page URL (Finding 14)
            if relative.name != "404.html":
                if relative == Path("index.html"):
                    expected_canonical = base_url
                elif relative.name == "index.html":
                    expected_canonical = f"{base_url}{relative.parent.as_posix()}/"
                else:
                    expected_canonical = f"{base_url}{relative.as_posix()}"
                if len(parser.canonicals) != 1 or parser.canonicals[0] != expected_canonical:
                    issues.append(f"{label} canonical URL must be exactly {expected_canonical} (found {parser.canonicals})")

            # Check unexpected noindex on production (Finding 14)
            is_expected_noindex = label in {"/404.html", "/thank-you/index.html"} or label in disabled_feature_paths
            has_noindex = any("noindex" in r for r in parser.robots)
            if has_noindex and not is_expected_noindex:
                issues.append(f"{label} has unexpected production noindex directive")

            # Check for leaked unverified/editorial placeholders shipping to production (Findings 1, 9)
            unverified_html_markers = [
                (">to confirm<", "contains unverified 'to confirm' flag"),
                (">To confirm<", "contains unverified 'To confirm' flag"),
                ("Representative visual", "contains placeholder work story marker"),
                ("Launch note: replace the representative", "contains internal launch instructions"),
                ("Unverified — visible on staging", "contains unverified warranty guarantee"),
                ("Confirm make, model", "contains unconfirmed equipment specification"),
                ("Confirm timeline", "contains unconfirmed project story timeline"),
            ]
            for marker, desc in unverified_html_markers:
                if marker in text and label not in disabled_feature_paths:
                    issues.append(f"{label} {desc}")

        # Check links and resources
        for target in parser.links + parser.resources:
            if not target:
                continue
            parsed_target = urlsplit(target)
            if target.startswith("//") or (parsed_target.scheme and parsed_target.scheme not in {"http", "https"}):
                continue
            if parsed_target.netloc and parsed_target.netloc != urlsplit(base_url).netloc:
                continue
            if parsed_target.path.startswith("/") and path_relative_to_base(parsed_target.path, base_url) is None:
                issues.append(f"{label} has a root-relative URL outside the configured site path: {target}")
                continue

            destination = output_path_for_url(build_dir, target, base_url, current_page=page)
            if destination is not None and not destination.is_file():
                issues.append(f"{label} points to a missing built path: {target}")
            elif destination is not None and parsed_target.fragment:
                # Fragment verification (Finding 14)
                target_parser_info = parsed_pages.get(destination)
                if target_parser_info:
                    dest_parser, _ = target_parser_info
                    if parsed_target.fragment not in dest_parser.ids:
                        issues.append(f"{label} has broken fragment link #{parsed_target.fragment} on {destination.relative_to(build_dir)}")

    # Audit robots.txt
    robots = build_dir / "robots.txt"
    if not robots.is_file():
        issues.append("robots.txt is missing")
    else:
        robots_text = robots.read_text(encoding="utf-8")
        if staging:
            if re.search(r"(?mi)^Disallow:\s*/\s*$", robots_text):
                issues.append("Public staging must allow crawlers to read noindex; use access control for private review")
            if "Sitemap:" in robots_text:
                issues.append("staging robots.txt must not advertise a sitemap")
        else:
            expected_sitemap = f"Sitemap: {base_url}sitemap.xml"
            if expected_sitemap not in robots_text:
                issues.append(f"robots.txt must advertise {expected_sitemap}")

    # Audit sitemap.xml
    sitemap = build_dir / "sitemap.xml"
    if staging and sitemap.is_file():
        issues.append("staging build must not include sitemap.xml")
    elif not staging and not sitemap.is_file():
        issues.append("sitemap.xml is missing")
    elif not staging:
        try:
            root = ElementTree.fromstring(sitemap.read_text(encoding="utf-8"))
            locations = [element.text or "" for element in root.iter() if element.tag.endswith("}loc")]
            if not locations:
                issues.append("sitemap.xml contains no URLs")
            expected = {p.canonicals[0] for page, (p, _) in parsed_pages.items()
                        if page.name != '404.html' and len(p.canonicals) == 1
                        and not any('noindex' in rule for rule in p.robots)}
            missing = expected - set(locations)
            for location in sorted(missing): issues.append(f'Indexable page missing from sitemap: {location}')
            for location in locations:
                if not location.startswith(base_url):
                    issues.append(f"sitemap URL is not absolute under the production URL: {location}")
                else:
                    destination = output_path_for_url(build_dir, location, base_url)
                    if destination is not None and not destination.is_file():
                        issues.append(f"sitemap contains a missing built path: {location}")
                if location.endswith("/thank-you/"):
                    issues.append("sitemap must not include the thank-you confirmation page")
                for disabled in disabled_feature_paths:
                    disabled_url_suffix = disabled.replace("/index.html", "/")
                    if location.endswith(disabled_url_suffix):
                        issues.append(f"sitemap includes URL for disabled feature: {location}")
        except ElementTree.ParseError as error:
            issues.append(f"sitemap.xml is not valid XML: {error}")

    # Audit search index (index.json)
    search_index = build_dir / "index.json"
    if not search_index.is_file():
        issues.append("index.json is missing")
    if search_index.is_file():
        try:
            index_data = json.loads(search_index.read_text(encoding="utf-8"))
            if not isinstance(index_data, list):
                issues.append("index.json must be a JSON array")
            else:
                if features.get('search') is False and index_data:
                    issues.append('Search disabled but index contains entries')
                seen_urls = set()
                for entry in index_data:
                    if not isinstance(entry, dict) or any(not isinstance(entry.get(k), str) for k in ('title','url','summary','text','section')):
                        issues.append('index.json contains malformed entry')
                        continue
                    url = entry['url']
                    destination = output_path_for_url(build_dir, url, base_url)
                    if destination is None or not destination.is_file():
                        issues.append(f'index.json contains missing destination: {url}')
                    if not url:
                        issues.append("index.json entry missing URL")
                    elif url in seen_urls:
                        issues.append(f"index.json contains duplicate entry: {url}")
                    seen_urls.add(url)

                    if url.endswith("/thank-you/"):
                        issues.append("index.json must not index the thank-you confirmation page")
                    for disabled in disabled_feature_paths:
                        disabled_url_suffix = disabled.replace("/index.html", "/")
                        if path_relative_to_base(urlsplit(url).path, base_url) == disabled_url_suffix:
                            issues.append(f"index.json contains disabled feature URL: {url}")
        except json.JSONDecodeError as err:
            issues.append(f"index.json is not valid JSON: {err}")

    # Feeds and JSON-LD must respect the same publication policy as HTML.
    for feed in build_dir.rglob('*.xml'):
        if feed.name == 'sitemap.xml':
            continue
        try:
            document = ElementTree.parse(feed)
            for item in document.findall('.//item'):
                link = item.findtext('link', '')
                route = path_relative_to_base(urlsplit(link).path, base_url)
                if route is None or route.rstrip('/') + '/index.html' in disabled_feature_paths:
                    issues.append(f'{feed.relative_to(build_dir)} exposes disabled or invalid feed content: {link}')
                if not features.get('blog'):
                    issues.append(f'{feed.relative_to(build_dir)} includes items while blog is off')
        except ElementTree.ParseError as error:
            issues.append(f'{feed.relative_to(build_dir)}: invalid XML ({error})')
    for page, (_, text) in parsed_pages.items():
        label = '/' + page.relative_to(build_dir).as_posix()
        blocks = re.findall(r'<script[^>]*type=[\"\']?application/ld\+json[\"\']?[^>]*>(.*?)</script>', text, re.S)
        for block in blocks:
            try:
                graph = json.loads(block)
                if label in disabled_feature_paths:
                    issues.append(f'{label}: disabled page exposes structured data')
                if not isinstance(graph, (dict, list)):
                    issues.append(f'{label}: invalid structured data shape')
            except json.JSONDecodeError:
                issues.append(f'{label}: malformed JSON-LD')

    # Audit home page form fallback
    home = build_dir / "index.html"
    if home.is_file():
        home_text = home.read_text(encoding="utf-8")
        home_parser = PageAudit()
        home_parser.feed(home_text)
        if home_parser.form_count != 1 or home_parser.brief_form_count != 1:
            issues.append("home page must contain exactly one project brief form")
        intake_enabled = CONFIG.get('params', {}).get('intake', {}).get('enabled') is True
        if ('data-online-intake' in home_text) != intake_enabled:
            issues.append('Generated form capability does not match intake configuration')
        if intake_enabled:
            for marker in ('data-request-consent', 'data-request-status', 'data-retry-request', 'data-request-revision', 'js/intake.'):
                if marker not in home_text:
                    issues.append('Online form missing required delivery control: ' + marker)
        if "JavaScript is required to prepare the brief" not in home_text:
            issues.append("project brief must include a no-JavaScript contact fallback")

    return issues


def main():
    global CONFIG
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--staging', action='store_true')
    parser.add_argument('--config', help='Explicit comma-separated Hugo config files')
    parser.add_argument('--report', type=Path, help='Save a JSON validation report')
    parser.add_argument('--destination', choices=['public'], help='Copy the verified artifact to public/ only on success')
    parser.add_argument('--fingerprints', action='store_true', help='Print required file hashes for owner review; never approves content')
    args = parser.parse_args()
    configs = args.config
    if not configs:
        try: configs = default_configs(ROOT, args.staging)
        except (ValueError, OSError) as error:
            print(f'FAIL: {error}'); return 1
    issues = []
    source_hashes = {}
    artifact_hashes = {}
    base_url = normalized_base_url(args.base_url)
    if base_url is None:
        issues.append('base-url must be a real absolute URL without credentials, query, or fragment')
    try:
        CONFIG = load_config(ROOT, configs)
        if args.fingerprints:
            print(json.dumps({name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in required_sources(ROOT, CONFIG) if (ROOT/name).is_file()}, indent=2))
            return 0
        if not args.staging and (not base_url or not base_url.startswith('https://') or normalized_base_url(CONFIG.get('params', {}).get('productionURL', '')) != base_url):
            issues.append('Production URL must match the owner-approved HTTPS params.productionURL')
        if not args.staging and git_value('rev-parse', 'HEAD') is None:
            issues.append('Release receipts must name a revision: initialize Git and commit this source before a production release')
        if not args.staging and git_value('status', '--porcelain') != '':
            issues.append('Production release requires a clean working tree, including untracked files; review and commit the intended source first')
        issues.extend(source_issues(ROOT, CONFIG, production=not args.staging))
        source_hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                         for name in [*required_sources(ROOT, CONFIG), 'data/evidence.json'] if (ROOT / name).is_file()}
        if not args.staging and CONFIG.get('params', {}).get('noindex') is not False:
            issues.append('Production config must explicitly set noindex = false')
        if args.staging and CONFIG.get('params', {}).get('noindex') is not True:
            issues.append('Staging config must explicitly set noindex = true')
    except (ValueError, TypeError, KeyError, OSError) as err:
        issues.append(f'Invalid configuration or content: {err}')
    with tempfile.TemporaryDirectory(prefix='jeff-does-doors-release-') as tmp:
        if base_url and CONFIG is not None and not issues:
            command = ['hugo','--panicOnWarning','--cacheDir',str(Path(tempfile.gettempdir()) / 'jeff-does-doors-hugo-cache'),'--config',configs,'--environment','staging' if args.staging else 'production','--baseURL',base_url,'--minify','--destination',tmp,'--cleanDestinationDir','--configDir',str(Path(tmp) / 'unused-config')]
            # Only the explicit, reviewed config files may control this build.
            # Ignore ambient Hugo overrides and implicit config directories.
            build_env = {key: value for key, value in os.environ.items() if not key.upper().startswith('HUGO_')}
            if not args.staging:
                build_env['HUGO_RELEASE_GATE'] = 'source-validated-v1'
            result = subprocess.run(command, cwd=ROOT, env=build_env, capture_output=True, text=True)
            if result.returncode:
                detail = (result.stderr or result.stdout).strip().splitlines()
                # Source failures already give exact owner actions; keep build diagnostics concise.
                issues.append('Hugo build blocked: ' + (detail[-1] if detail else 'unknown error'))
            else:
                issues.extend(audit_build(Path(tmp), base_url, staging=args.staging))
                artifact_hashes = {path.relative_to(tmp).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in sorted(Path(tmp).rglob('*')) if path.is_file()}
                current_sources = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                   for name in [*required_sources(ROOT, CONFIG), 'data/evidence.json'] if (ROOT / name).is_file()}
                if source_hashes != current_sources:
                    issues.append('Source changed during the build; discard this artifact and run the gate again')
                if not args.staging and git_value('status', '--porcelain') != '':
                    issues.append('Working tree changed during the production build; discard this artifact')
        report = {'status':'blocked' if issues else 'passed', 'environment':'staging' if args.staging else 'production',
                  'config':configs, 'baseURL':base_url, 'checkedAt':datetime.now(timezone.utc).isoformat(),
                  'commit':git_value('rev-parse','HEAD'),
                  'workingTreeDirty':(lambda s: None if s is None else bool(s))(git_value('status','--porcelain')),
                  'sourceHashes':source_hashes, 'artifactHashes':artifact_hashes,
                  'manifestNote':'SHA-256 inventories identify bytes; release.json is excluded from artifactHashes. These are not digital signatures or deployment evidence.',
                  'hugo':subprocess.run(['hugo','version'],capture_output=True,text=True).stdout.strip(),
                  'issues':issues}
        if args.report:
            args.report.write_text(json.dumps(report,indent=2)+'\n')
        if not issues and args.destination:
            destination = ROOT / args.destination
            if destination.is_symlink():
                raise ValueError('Refusing symlink output directory')
            temp_swap = destination.parent / f".tmp-{destination.name}-{uuid.uuid4().hex}"
            backup = None
            try:
                shutil.copytree(tmp, temp_swap)
                (temp_swap / 'release.json').write_text(json.dumps(report, indent=2) + '\n')
                if destination.exists():
                    backup = destination.parent / f".bak-{destination.name}-{uuid.uuid4().hex}"
                    destination.rename(backup)
                temp_swap.rename(destination)
                if backup and backup.exists():
                    shutil.rmtree(backup)
            except Exception:
                if temp_swap.exists():
                    shutil.rmtree(temp_swap, ignore_errors=True)
                if backup and backup.exists() and not destination.exists():
                    backup.rename(destination)
                raise
    if issues:
        print(f'FAIL: {len(issues)} blocker(s)')
        for issue in issues: print('- ' + issue)
        return 1
    print('PASS: ' + report['environment'] + ' source policy and generated artifact checks')
    return 0


if __name__ == '__main__':
    sys.exit(main())
