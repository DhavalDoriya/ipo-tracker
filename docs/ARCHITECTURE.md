# Architecture

## Stack
| Part | Choice | Reason |
| --- | --- | --- |
| Site | Astro 7, static output, plain CSS | Zero JS by default, fast pages, no framework needed |
| Language | TypeScript (strict) | Typed data loaders catch schema drift at build |
| Data | JSON files in `data/` | No database to run or pay for; git is the history |
| Scraper | Python 3 + requests + BeautifulSoup | Small, well known, runs free in Actions |
| Automation | GitHub Actions | Cron + deploy on the free tier |
| Hosting | GitHub Pages | Free static hosting |

## System
```
GitHub Actions cron ──> scripts/scrape.py ──> data/*.json ──> validate.py
                                                  │ (commit only if changed)
                                                  ▼
                               deploy.yml: astro build ──> GitHub Pages
```

## Folder rules
- `data/`: JSON only. Written by the scraper or by hand. The site never writes here.
- `scripts/`: Python only. Never imports from or depends on `src/`.
- `src/lib/`: the only place that reads `data/` (`data.ts`) or formats values (`format.ts`).
- `src/components/`: presentational; receive data as props, never read files.
- `src/pages/`: load data through `src/lib/data.ts` and compose components.
- `docs/`: decisions. Update the doc in the same change as the decision.

## One request, end to end
1. Cron fires `update-data.yml`; `scrape.py` fetches sources and builds the IPO list.
2. If the content differs from `data/ipos.json` it writes the file (with a new `updated_at`) and a daily copy in `data/history/`.
3. `validate.py` checks every data file; on failure the job stops with nothing committed.
4. The job commits `data/`, pushes, and calls `deploy.yml`.
5. `astro build` reads `data/*.json` through `src/lib/data.ts` and renders static HTML.
6. Pages serves `dist/`. The visitor's browser gets plain HTML and one small filter script.

## Environments
| Env | How | URL |
| --- | --- | --- |
| Local | `npm run dev` | `http://localhost:4321/ipo-tracker/` |
| Production | `deploy.yml` | `https://<user>.github.io/ipo-tracker/` |

`SITE_URL` and `BASE_PATH` env vars override the defaults in `astro.config.mjs`.

## Boundaries
- Pages -> `lib/data.ts` -> `data/*.json`. Components do not touch the file system.
- Internal links always go through `url()` in `src/lib/url.ts` so the base path is never hard-coded.
- Client JavaScript is limited to the filter script. No client-side data fetching.

## Decision log
| Decision | Why |
| --- | --- |
| Repo and base path are `ipo-tracker` (deploy base follows the repo name via `BASE_PATH`) | Wrong base path = no CSS on Pages |
| Node 24 in CI | Astro 7 requires Node >= 22.23 |
| `update-data.yml` calls `deploy.yml` via `workflow_call` | Pushes made with `GITHUB_TOKEN` do not trigger other workflows |
| Scraper writes nothing when content is unchanged | Avoids a commit and deploy every day |
| Build-time data only | Keeps pages static and fast; freshness comes from redeploys |
| No UI framework, no Tailwind | Nothing here needs them; fewer moving parts |
| `ipos.json` comes from Groww's public IPO page (data embedded in the page HTML) | Owner's decision (12 Nov 2026): the data is publicly viewable. robots.txt allows the page and it answers a plain request. Groww's terms prohibit copying without consent, so this is an accepted risk: if Groww objects, remove the source |
| `coming_soon.json` comes from SEBI's public issue filing lists | Regulator's own public record; robots.txt allows it; plain HTML with an honest User-Agent |
| NSE, BSE, Chittorgarh, InvestorGain, Zerodha not used | They need cookies / a browser User-Agent or refuse the scraper's robots.txt request |
| Moneycontrol, Upstox not used | Their terms prohibit scrapers or reuse, and their plain HTML carries less than Groww's (Moneycontrol loads open and upcoming IPOs from a private API) |
| Never call a site's private API or imitate a browser | That is bypassing access controls, not reading a public page |
