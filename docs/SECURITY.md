# Security

## Data held
Public market data only. No accounts, no forms that submit anywhere, no cookies, no analytics, no personal data (never PAN, demat or contact details).

## Roles
- **Visitor**: read-only static pages.
- **Maintainer**: write access to the GitHub repo.
- **Actions bot**: `contents: write` in `update-data.yml` only, to commit `data/`.

## Secrets
None are needed. If one is ever added it lives in GitHub Secrets (CI) or `.env.local` (local, git-ignored). Never in the repo.

## Input handling
- The only untrusted input is scraped HTML. It is parsed to plain values, checked by `scripts/validate.py`, and rendered by Astro, which escapes output. Never use `set:html` with data from `data/`.
- `source_url` values must start with `https://`; the validator enforces it. External links use `rel="noopener noreferrer"`.
- The filter script reads from the DOM only and never writes HTML.

## Scraper rules
- `robots.txt` is always obeyed (the scraper enforces it). Read each source's terms before adding it; using a source whose terms forbid reuse is the owner's decision and is recorded in the ARCHITECTURE decision log.
- At most 1 request per second, with an identifying User-Agent.
- No logins, no CAPTCHA bypass, no private API endpoints, no browser-imitating headers or cookies.

## CI rules
- Workflows declare the minimum `permissions`.
- Actions are pinned to a major version from `actions/*` only.
- The scraper job never runs code fetched from a scraped page.

## Dependencies
Ask before adding one. Keep `package-lock.json` committed; run `npm audit` before releases.

## Logging
Scraper logs URLs and counts only.

## Pre-merge checklist (OWASP Top 10:2025)
- [ ] A01 Broken access control: no new workflow permission beyond what is needed.
- [ ] A02 Security misconfiguration: no debug output or source maps of secrets; Pages serves `dist/` only.
- [ ] A03 Software supply chain failures: no new dependency without approval; lockfile updated.
- [ ] A04 Cryptographic failures: all source and outbound URLs are `https`.
- [ ] A05 Injection: no `set:html` / `innerHTML` with scraped data.
- [ ] A06 Insecure design: feature does not require collecting personal data.
- [ ] A07 Authentication failures: not applicable (no auth); confirm none was added.
- [ ] A08 Software or data integrity failures: `validate.py` passes; data commits come only from the workflow or a reviewed change.
- [ ] A09 Logging and alerting failures: a failed scrape fails the job visibly.
- [ ] A10 Mishandling of exceptional conditions: scraper failure leaves existing data untouched.
