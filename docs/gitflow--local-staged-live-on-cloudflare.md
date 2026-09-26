# Local → GitHub Pages staging → production

Status: workflows and local validation are implemented. Remote Pages settings, current deployments, Cloudflare configuration, domain/DNS, and production authorization must be verified separately. This document does not claim any remote deployment happened.

## Environment contract

| Surface | Config | Publication behavior |
| --- | --- | --- |
| Review | `hugo.toml,profiles/jeff-does-doors.toml,hugo-staging.toml` | Full preview with example contacts; noindex/nofollow; no sitemap/RSS |
| Proposed launch | `hugo.toml,profiles/jeff-does-doors.toml,hugo-launch.toml` | Smaller feature set; real contact/domain and revision-bound approvals required |
| Custom production selection | Explicit `--config` list | Same source and artifact gate; every selected config participates in evidence |

A disabled feature retains a neutral noindex route. Its original content is excluded from bodies, search, sitemap, feed items, and structured data. Staging is public if deployed: noindex is not authentication.

## Local development

Use Hugo 0.166.0 extended and the dependencies from [README](../README.md).

```sh
git status --short --branch
bash scripts/preview.sh   # hugo.toml,profiles/jeff-does-doors.toml,hugo-staging.toml on port 1317
```

Use temporary output for inspection, or the validated artifact command. Do not edit generated `public/` or `resources/` files. See [verification](verification.md) for targeted checks.

## Git review and staging

Preserve unrelated working-tree changes. Review staged and unstaged changes separately. Stage, commit, and push only when Ryan delegates those actions.

The pull-request workflow runs focused regressions and the staging gate. The Pages workflow triggers on authorized pushes to `main` or an authorized manual dispatch. It installs the pinned Hugo and Python dependencies, validates a temporary build, copies that same artifact to `public/`, uploads it, and uses `actions/deploy-pages`.

This is an Actions artifact deployment, not a `gh-pages` branch. Repository Pages settings must select GitHub Actions. Verify the actual deployed URL, commit, noindex behavior, and visitor interactions after deployment.

## Production readiness

1. Select the launch features and confirm the actual business facts.
2. Enter the production HTTPS URL in `params.productionURL` in the selected config.
3. Replace placeholder contacts and media. Complete the [owner evidence](launch-inputs.md).
4. Run:

```sh
.venv/bin/python scripts/release_check.py --base-url "$LIVE_SITE_URL" --destination public --report /tmp/jeff-release.json
```

The URL must match the approved configuration. On success, `public/` contains the exact audited artifact and `release.json`. The receipt records source commit, working-tree state, toolchain, environment, and check time; it does not prove deployment or customer delivery. A release is refused outright when Git cannot name a revision, so the receipt never records a placeholder commit. On failure, the command does not replace a previously generated artifact. **Do not deploy an old artifact after a failed gate.**

This release command is the required production entry point. Direct indexable
production Hugo builds are blocked. Only the explicit `--config` files control
release builds; ambient `HUGO_*` overrides and implicit `config/` directories are
ignored. The command invokes Hugo only after source policy passes and supplies
its internal workflow marker. Do not set that marker manually.

For a production release, require a reviewed clean commit and retain the report with deployment records. Review authority does not imply push or deployment authority.

## Cloudflare activation (owner-controlled, pending)

Before connecting a production target, choose the exact project, branch, domain, and preview policy. `main` currently serves the staging workflow; do not accidentally make routine staging updates automatically publish live.

Configure the production build to install `requirements.txt`, then run `scripts/release_check.py --base-url "$LIVE_SITE_URL" --destination public`. Use `public` as output. Set Hugo to 0.166.0 extended. Do not run an unvalidated second Hugo build after the gate. Require the source checks before publication. Preview deployments must use staging configuration and must not expose private evidence.

Verify current provider setup steps against [Cloudflare's Hugo guide](https://developers.cloudflare.com/pages/framework-guides/deploy-a-hugo-site/), [branch controls](https://developers.cloudflare.com/pages/configuration/branch-build-controls/), and [custom-domain guidance](https://developers.cloudflare.com/pages/configuration/custom-domains/) at activation time. Provider account changes, DNS changes, and deployment require explicit authorization.

## Live acceptance and recovery

Record deployed commit, deployment identifier, URL, and artifact receipt. Verify HTTPS, correct canonical URLs, crawl policy, sitemap, a missing-page response, mobile navigation, and real device handoffs. If online delivery is ever added, verify the actual destination separately.

For recovery, identify a previously verified production deployment and follow the provider's current rollback procedure with authorization. Preserve the Git history and follow with a source correction. Verify the restored site; a dashboard success message alone is insufficient. [Cloudflare rollback guidance](https://developers.cloudflare.com/pages/configuration/rollbacks/)

Maintenance owner: Ryan for implementation and technical checks; Jeff for business facts and operational promises. Reconfirm ownership if the team changes.

## Profile selection and crawl controls

The Python tools resolve their default profile from `site-profile.json`. Hugo commands require an explicit `profiles/jeff-does-doors.toml`; `scripts/preview.sh` supplies it. Review and launch selections are separate configurations of the same source.

Staging emits HTML noindex and crawlable robots so crawlers can read that directive. Robots controls apply at an origin root: a GitHub Pages project path cannot override its host root robots file. Confirm the host policy separately. Noindex is not privacy; use authentication/access restrictions for a private preview. Do not block crawling and assume crawlers can still discover the page-level noindex.

## Optional online intake

The implementation and environment-specific activation procedure are in [site operations](site-operations.md). Keep intake disabled on GitHub Pages. The same approved source revision must supply both the audited static artifact and Cloudflare Functions.
