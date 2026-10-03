"""Shared source policy: standard parsing, feature registry, and revision-bound approvals."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import yaml
try:
    import tomllib
except ImportError:
    import tomli as tomllib


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def parse_yaml(text):
    try:
        return yaml.load(text, Loader=UniqueLoader)
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML: {error}") from error


def merge(left, right):
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(left.get(key), dict):
            merge(left[key], value)
        else:
            left[key] = value
    return left


def load_config(root, files):
    config = {}
    for name in files.split(','):
        with (root / name).open('rb') as stream:
            merge(config, tomllib.load(stream))
    config["_configFiles"] = files.split(",")
    return config


def default_configs(root, staging=False):
    selection = json.loads((root / 'site-profile.json').read_text())
    profile = selection.get('profile', '')
    if not isinstance(profile, str) or not re.fullmatch(r'profiles/[a-z0-9-]+\.toml', profile) or not (root / profile).is_file():
        raise ValueError('site-profile.json must select an existing profiles/<slug>.toml file')
    return ','.join(['hugo.toml', profile, 'hugo-staging.toml' if staging else 'hugo-launch.toml'])

def registry(root):
    return json.loads((root / 'data/publishing.json').read_text())


def enabled(name, flags, definitions, seen=()):
    if name in seen or name not in definitions:
        return False
    return flags.get(name) is True and all(enabled(dep, flags, definitions, (*seen, name)) for dep in definitions[name]['requires'])


def frontmatter(path):
    text = path.read_text()
    match = re.match(r'\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)', text, re.DOTALL)
    if not match:
        raise ValueError(f'{path.name}: YAML front matter required')
    data = parse_yaml(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f'{path.name}: front matter must be a mapping')
    return data


def page_feature(path, data, definitions):
    if data.get('feature'):
        return data['feature']
    for name, definition in definitions.items():
        if len(path.parts) > 1 and path.parts[0] in definition['sections']:
            return name
    return None


def required_sources(root, config):
    policy = registry(root)
    flags = config.get('params', {}).get('features', {})
    sources = set(policy['core'])
    # Rendering code can introduce claims anywhere, including unregistered partials.
    # Technical review covers code; business review covers facts. Neither is inferred.
    sources.update({'data/publishing.json', 'data/specialties.yaml', 'assets/contracts/brief-schema.json', 'assets/contracts/survey-schema.json', 'data/door-guidance.json', 'site-profile.json', 'static/_headers', 'static/_routes.json', 'data/intake-acceptance.json', 'requirements.txt'})
    for directory in ('layouts', 'assets', 'static', 'functions', 'lib', 'migrations', 'scripts', '.github/workflows'):
        for path in (root / directory).rglob('*'):
            if not path.is_file() or path.name == '.DS_Store' or path.name.startswith('.') or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            if directory == 'static' and path.name.startswith('_'):
                continue
            sources.add(path.relative_to(root).as_posix())
    # Optional deployment routing is still executable publication behavior.
    if (root / 'static/_redirects').is_file():
        sources.add('static/_redirects')
    sources.update(config.get('_configFiles', []))
    for name, definition in policy['features'].items():
        if enabled(name, flags, policy['features']):
            sources.update(definition['sources'])
    # Discover active content as well as registered content; new pages cannot evade approval.
    for path in (root / 'content').rglob('*.md'):
        data = frontmatter(path)
        flag = page_feature(path.relative_to(root / 'content'), data, policy['features'])
        if not data.get('reviewOnly') and (not flag or enabled(flag, flags, policy['features'])):
            sources.add(path.relative_to(root).as_posix())
    for name in list(sources):
        path = root / name
        if not path.is_file():
            continue
        for image in re.findall(r'images/[A-Za-z0-9_./-]+\.(?:webp|png|jpg|jpeg|svg)', path.read_text(errors='ignore')):
            sources.add('static/' + image)
    return sorted(sources)


def approval_issues(root, sources):
    evidence = json.loads((root / 'data/evidence.json').read_text())
    issues = []
    today = dt.date.today()
    for name in sources:
        path = root / name
        if not path.is_file():
            issues.append(f'{name}: required source missing')
            continue
        item = evidence.get(name, {})
        if not isinstance(item, dict) or item.get('approved') is not True:
            issues.append(f'{name}: owner approval pending in data/evidence.json')
            continue
        if item.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
            issues.append(f'{name}: content changed since approval; re-review this revision')
        if not isinstance(item.get('reviewer'), str) or not item['reviewer'].strip():
            issues.append(f'{name}: approval needs a reviewer')
        if not isinstance(item.get('sources'), list) or not item['sources'] or any(not isinstance(s,str) or not s.strip() for s in item['sources']):
            issues.append(f'{name}: approval needs source references')
        try:
            reviewed = dt.date.fromisoformat(item.get('reviewedOn', ''))
            if reviewed > today:
                raise ValueError('future review date')
            if item.get('reviewAfter') and dt.date.fromisoformat(item['reviewAfter']) < today:
                issues.append(f'{name}: scheduled review is overdue')
        except (ValueError, TypeError):
            issues.append(f'{name}: approval dates must be valid, non-future ISO review dates')
    return issues


# Explicit schemas for rendered records. File approval covers all copy, including
# fields not used as publication switches (biographies, accepted methods, etc.).
LIST_SCHEMAS = {
 'services': (None, ['id','path','title','summary','bullets'], None),
 'process': (None, ['step','title','body'], None),
 'faqs': (None, ['category','items'], None),
 'stats': (None, ['value','label'], ('verified', True)),
 'credentials': (None, ['title','body'], ('verified', True)),
 'team': (None, ['name','role','bio','image','alt'], ('placeholder', False)),
 'gallery': (None, ['image','alt','caption','tag'], ('placeholder', False)),
 'equipment': (None, ['name','detail','spec'], ('verified', True)),
 'pricing': ('rows', ['service','range','drivers'], ('verified', True)),
 'financing': ('options', ['title','body'], ('verified', True)),
 'jobs': ('positions', ['title','type','detail','requirements'], None),
 'reviews': (None, ['quote','name','context','url','date'], ('approved', True)),
}


def data_issues(name, data, production):
    issues = []
    def walk(value, location):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {'verified','approved','placeholder','active','open','featured'} and type(child) is not bool:
                    issues.append(f'{location}.{key}: must be a boolean, not {type(child).__name__}')
                walk(child, f'{location}.{key}')
        elif isinstance(value, list):
            for n, child in enumerate(value): walk(child, f'{location}[{n}]')
    walk(data, name)
    stem = Path(name).stem
    if stem in LIST_SCHEMAS:
        child, fields, approval = LIST_SCHEMAS[stem]
        records = data.get(child) if child and isinstance(data, dict) else data if not child else None
        if not isinstance(records, list) or not records:
            return issues + [f'{name}: expected nonempty {child or "record"} list']
        for i, item in enumerate(records, 1):
            if not isinstance(item, dict):
                issues.append(f'{name} #{i}: expected mapping'); continue
            for field in fields:
                if field == 'date' and not production: continue
                if field not in item or item[field] is None or item[field] == '' or item[field] == []:
                    issues.append(f'{name} #{i}: missing {field}')
            if approval:
                key, expected = approval
                if type(item.get(key)) is not bool or (production and item[key] is not expected):
                    issues.append(f'{name} #{i}: requires {key}: {str(expected).lower()} for publication')
            if stem == 'jobs' and production and item.get('open') is True and item.get('verified') is not True:
                issues.append(f'{name} #{i}: open role needs verified: true')
            if stem == 'reviews' and production:
                try:
                    day = dt.date.fromisoformat(str(item.get('date','')))
                    if day > dt.date.today(): raise ValueError()
                except ValueError:
                    issues.append(f'{name} #{i}: needs an evidenced, valid publication date')
            if stem == 'faqs':
                questions = item.get('items')
                if not isinstance(questions, list) or not questions:
                    issues.append(f'{name}: FAQ items must be a nonempty list')
                    continue
                for question in questions:
                    if not isinstance(question, dict) or not question.get('question') or not question.get('answer'):
                        issues.append(f'{name}: each FAQ needs a question and answer')
    elif stem == 'service_area':
        if not isinstance(data, dict): return issues + [f'{name}: expected mapping']
        if production and data.get('verified') is not True: issues.append(f'{name}: requires verified: true')
        for group in ('primary', 'extended'):
            towns = data.get(group, {}).get('towns') if isinstance(data.get(group), dict) else None
            if not isinstance(towns, list):
                issues.append(f'{name}.{group}: towns list required'); continue
            for town in towns:
                if not isinstance(town, dict) or any(not isinstance(town.get(k),str) or not town[k].strip() for k in ('name','state','county')):
                    issues.append(f'{name}.{group}: each town needs name, state, county')
    elif stem in {'promo','warranty'}:
        if not isinstance(data, dict): return issues + [f'{name}: expected mapping']
        if production and (stem != 'promo' or data.get('active') is True) and data.get('verified') is not True:
            issues.append(f'{name}: requires verified: true')
    return issues



def profile_issues(root, config, production):
    """Validate reusable profile/catalog relationships before rendering."""
    issues = []
    params = config.get('params', {})
    services = parse_yaml((root / 'data/services.yaml').read_text())
    specialties = parse_yaml((root / 'data/specialties.yaml').read_text())
    if not isinstance(services, list) or not all(isinstance(x, dict) for x in services):
        return ['services: expected a list of records']
    ids = [x.get('id') for x in services]
    paths = [x.get('path') for x in services]
    for field, values in [('id', ids), ('path', paths)]:
        if any(not isinstance(x, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', x) for x in values):
            issues.append(f'services: invalid {field}; use unique lowercase slugs')
        elif len(values) != len(set(values)):
            issues.append(f'services: duplicate {field}')
    for page in (root / 'content/services').glob('*.md'):
        if page.name != '_index.md' and frontmatter(page).get('serviceID') not in ids:
            issues.append(f'{page.name}: unknown serviceID')
    for page in (root / 'content/blog').glob('*.md'):
        service = frontmatter(page).get('service')
        if page.name != '_index.md' and service not in ids:
            issues.append(f'{page.name}: link the guide to an offered service')
    for service in services:
        path = service.get('path')
        if not isinstance(path, str) or not re.fullmatch(r'[a-z0-9-]+', path): continue
        page = root / 'content/services' / (path + '.md')
        if not page.is_file() or frontmatter(page).get('serviceID') != service.get('id'):
            issues.append(f'services.{service.get("id")}: matching service page required')
        for field in ('title', 'summary'):
            if not isinstance(service.get(field), str) or not service[field].strip():
                issues.append(f'services.{service.get("id")}: {field} must be text')
        for field in ('bullets', 'questions', 'relatedServices'):
            if field in service and not isinstance(service[field], list):
                issues.append(f'services.{service.get("id")}: {field} must be a list')
        for related in service.get('relatedServices', []) if isinstance(service.get('relatedServices', []), list) else []:
            if related not in ids: issues.append(f'services.{service.get("id")}: unknown related service {related}')
        for question in service.get('questions', []) if isinstance(service.get('questions', []), list) else []:
            if not isinstance(question, dict) or not all(isinstance(question.get(k), str) and question[k].strip() for k in ('question', 'answer')):
                issues.append(f'services.{service.get("id")}: malformed question')
    selected = specialties.get(params.get('specialty')) if isinstance(specialties, dict) else None
    if not isinstance(selected, dict):
        issues.append('Profile must select a known specialty')
    else:
        order = selected.get('serviceOrder')
        if not isinstance(order, list) or any(not isinstance(x, str) or x not in ids for x in order) or len(order) != len(set(order)):
            issues.append('Specialty serviceOrder must contain unique known service IDs')
        if not isinstance(order, list): order = []
        if selected.get('primaryService') not in ids:
            issues.append('Specialty primaryService must reference an offered service')
    if params.get('brandTone', 'amber') not in {'amber', 'clay', 'slate'}:
        issues.append('brandTone must be amber, clay, or slate')
    for field in ('companyName', 'profileID', 'serviceArea', 'description'):
        if not isinstance(params.get(field), str) or not params[field].strip():
            issues.append(f'Profile requires {field}')
    for field in ('supportsSMS', 'emergencySupportsSMS', 'publicAddress', 'coverageConfirmed', 'draftRecovery', 'loadWebFonts'):
        if type(params.get(field)) is not bool: issues.append(f'{field}: explicit boolean required')
    if production and params.get('coverageConfirmed') is not True:
        issues.append('Confirm the business base and service coverage before publication')
    if production and not params.get('contactResponse'):
        issues.append('Confirm how inquiries are handled in params.contactResponse')
    for field in ('mapURL', 'reviewURL', 'reviewRequestURL', 'facebookURL', 'instagramURL'):
        value = params.get(field, '')
        if value:
            parsed = urlsplit(value) if isinstance(value, str) else None
            if not parsed or parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password:
                issues.append(f'{field}: use an absolute HTTPS URL without credentials')
    declared = params.get('approvalConfigFiles', [])
    if production and (not isinstance(declared, list) or set(declared) != set(config.get('_configFiles', []))):
        issues.append('approvalConfigFiles must list the exact selected config files')
    return issues

def source_issues(root, config, production=True):
    issues = []
    policy = registry(root)
    params = config.get('params', {})
    flags = params.get('features', {})
    issues.extend(profile_issues(root, config, production))
    for name in policy['features']:
        if type(flags.get(name)) is not bool:
            issues.append(f'features.{name}: explicit boolean required')
    for name in flags:
        if name not in policy['features']: issues.append(f'Unknown feature: {name}')
    for path in (root / 'content').rglob('*.md'):
        data = frontmatter(path)
        flag = page_feature(path.relative_to(root / 'content'), data, policy['features'])
        if flag and flag not in policy['features']: issues.append(f'{path.relative_to(root)}: unknown feature {flag}')
    sources = required_sources(root, config)
    for name in sources:
        path = root / name
        if not path.is_file():
            issues.append(f'{name}: required file missing'); continue
        if path.suffix == '.yaml':
            issues.extend(data_issues(name, parse_yaml(path.read_text()), production))
        elif path.suffix == '.md':
            data = frontmatter(path)
            for field in ['title','description']:
                if not isinstance(data.get(field), str) or not data[field].strip(): issues.append(f'{name}: {field} required')
            if production and path.parent.name == 'blog' and path.name != '_index.md':
                for field in ('date', 'lastmod', 'author', 'reviewedBy'):
                    if not data.get(field): issues.append(f'{name}: actual publication metadata required: {field}')
                for field in ('date', 'lastmod'):
                    if data.get(field):
                        try:
                            day = dt.date.fromisoformat(str(data[field])[:10])
                            if day > dt.date.today(): raise ValueError()
                        except ValueError: issues.append(f'{name}: invalid or future {field}')
            if production and path.parent.name == 'projects' and data.get('placeholder') is not False:
                issues.append(f'{name}: project story still illustrative')
    intake = params.get('intake', {})
    if intake.get('enabled'):
        if intake.get('enabled') is not True or intake.get('environment') not in ('local', 'preview', 'production'):
            issues.append('Online intake requires an explicit environment and boolean enabled')
        if any(not isinstance(intake.get(k), str) or not intake[k].strip() for k in ('siteKey', 'consentVersion', 'retentionNotice')):
            issues.append('Online intake requires siteKey, consentVersion, and retentionNotice')
        if intake.get('environment') != 'local' and re.fullmatch(r'[123]x0+(AA|AB|BB|FF)', intake.get('siteKey', '')):
            issues.append('Deployed intake cannot use a Turnstile test key')
        if production or intake.get('environment') == 'production':
            record = json.loads((root / 'data/intake-acceptance.json').read_text())
            tested_on = record.get('testedOn', '')
            valid_date = False
            try:
                if tested_on and dt.date.fromisoformat(str(tested_on)) <= dt.date.today():
                    valid_date = True
            except ValueError:
                pass
            evidence_list = record.get('evidence')
            valid_evidence = (
                isinstance(evidence_list, list)
                and len(evidence_list) > 0
                and all(isinstance(e, str) and e.strip() for e in evidence_list)
            )
            if (
                intake.get('environment') != 'production'
                or record.get('status') != 'accepted'
                or not valid_date
                or not valid_evidence
                or any([
                    record.get('baseURL') != params.get('productionURL'),
                    record.get('profile') != params.get('profileID'),
                    record.get('consentVersion') != intake.get('consentVersion'),
                ])
            ):
                issues.append('Production intake acceptance is pending for this site and notice revision')
    if production:
        issues.extend(approval_issues(root, sources))
        phone, email = params.get('contactPhone',''), params.get('contactEmail','')
        if 'example.' in email or '55501' in re.sub(r'\D','',phone): issues.append('Placeholder contacts cannot be published')
        if not phone and not email: issues.append('Direct business phone or email is required')
        if phone and not re.fullmatch(r'[\d\s+().-]{10,}', phone): issues.append('Invalid contactPhone')
        if phone and len(re.sub(r'\D','',phone)) < 10: issues.append('contactPhone needs at least 10 digits')
        if email and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email): issues.append('Invalid contactEmail')
        if enabled('emergency', flags, policy['features']) and not params.get('emergencyPhone'):
            issues.append('Emergency feature requires a confirmed emergencyPhone')
        if params.get('formEndpoint'):
            issues.append('Online delivery is not enabled: a selected provider and end-to-end acceptance test are required; use direct handoffs')
    return issues
