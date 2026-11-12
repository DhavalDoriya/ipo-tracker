# IPO Update

A free, static IPO information portal for the Indian market: mainboard and SME IPOs, a buyback calendar, and a 14-point analysis checklist. Built with Astro, fed by JSON files, refreshed by a scheduled Python scraper in GitHub Actions, hosted on GitHub Pages.

> For information only. Not financial advice. Verify everything with NSE, BSE and the registrar.

The IPO cards currently show **sample data** (placeholder companies); the pipeline list on the home page is real, from SEBI filings. See [Data sources](#data-sources).

## Local development

Requires Node 22.23+ (24 recommended) and Python 3.11+.

```bash
npm install
```

```bash
npm run dev
```

Open `http://localhost:4321/ipo-update/`.

Checks:

```bash
npm run check
```

```bash
npm run build
```

```bash
python3 scripts/validate.py
```

```bash
python3 -m unittest discover -s scripts/tests
```

The scraper tests need `pip install -r scripts/requirements.txt` (use a virtualenv).

## How updates work

1. `update-data.yml` runs every 30 minutes (and on demand).
2. `scripts/scrape.py` reads the sources in `scripts/sources.json`, checks each site's `robots.txt`, fetches at most one page per second, and builds the IPO list.
3. If the content is unchanged it writes nothing. Otherwise it writes `data/ipos.json` and a daily copy in `data/history/`.
4. `scripts/validate.py` checks every data file. Any error stops the run with nothing committed.
5. The workflow commits `data/` and calls `deploy.yml`, which builds the site and publishes it to Pages.

Editing a file in `data/` by hand and pushing to `main` deploys the same way.

## Data sources

`scripts/sources.json` has two lists:

- `filings`: regulator filing lists that feed `data/coming_soon.json` (the pipeline list on the home page). Configured with SEBI's public issue filings, RHP and DRHP stage. SEBI's `robots.txt` allows access and the pages are plain HTML.
- `sources`: HTML tables that feed `data/ipos.json` (the IPO cards). **Empty.** Every candidate checked was ruled out: NSE, BSE, Chittorgarh, InvestorGain and Zerodha need cookies or a browser-like User-Agent, or refuse the scraper's `robots.txt` request; Moneycontrol, Groww and Upstox prohibit scrapers or reuse in their terms. Until you have permission from a provider, edit `data/ipos.json` by hand (remove `"sample": true` when the data is real).

To add an IPO table source:

1. Confirm the site's `robots.txt` and terms of use allow automated access. Sites that need cookies, a browser-like User-Agent or a CAPTCHA to respond do not qualify.
2. Copy an entry from `scripts/sources.example.json` into `scripts/sources.json` and set the URL, table selector, date format and column headings.
3. Run `python3 scripts/scrape.py` then `python3 scripts/validate.py` locally.

The first successful run replaces the sample data and removes the sample banner.

Hand-maintained files: `data/gmp.json`, `data/ipos.json` (for now), `data/buybacks.json`, `data/checklists/*.json`. To add a checklist, copy `data/checklists/ipo-analysis-template.json` to `<slug>.json`, set `company` and `ipo_id`, and fill in each `analysis`.

Field reference: [docs/DATABASE.md](docs/DATABASE.md).

## Deploying to GitHub Pages

1. Create a public repository named `ipo-update` and push `main`.
2. Settings -> Pages -> Source: **GitHub Actions**.
3. If the repository name or owner differs, set repository variables or edit the defaults in `astro.config.mjs` (`SITE_URL`, `BASE_PATH`).

## Known limitations

- **GMP is not automated.** There is no reliable free public feed; enter it in `data/gmp.json` or leave it out.
- **Subscription data is a snapshot**, refreshed every 30 to 60 minutes at best. GitHub can delay scheduled runs.
- **Scrapers are fragile.** When a source changes its HTML the job fails and the last good data stays up. Watch the Actions tab.
- **No allotment lookup, broker integration or accounts.** These need a server and partner access.
- GitHub pauses scheduled workflows after 60 days without repository activity.

## Project docs

Start at [AGENTS.md](AGENTS.md). Decisions live in [docs/](docs/).

## Licence

Code: [MIT](LICENSE). Written content: CC BY 4.0.
