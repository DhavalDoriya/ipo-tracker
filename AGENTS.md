# AGENTS.md

Static IPO information portal for the Indian market. Astro 7 site built from JSON in `data/`, refreshed by a Python scraper in GitHub Actions, hosted on GitHub Pages. No backend, no database, no cost.

## Read first
| Task | Doc |
| --- | --- |
| New feature / behaviour change | [docs/PRD.md](docs/PRD.md) |
| Any UI or styling | [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) |
| New module, page, folder, workflow | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Data files and their fields | [docs/DATABASE.md](docs/DATABASE.md) |
| Scraper sources, workflows, links | [docs/SECURITY.md](docs/SECURITY.md) |
| Writing any code | [docs/CODE_STYLE.md](docs/CODE_STYLE.md) |
| Before saying a task is done | [docs/TESTING.md](docs/TESTING.md) |

## Map
| Path | What |
| --- | --- |
| `data/` | JSON the site is built from |
| `scripts/` | `scrape.py`, `validate.py`, tests |
| `src/lib/` | `data.ts` (loaders + types), `format.ts`, `url.ts` |
| `src/components/`, `src/layouts/`, `src/pages/` | Astro UI |
| `src/styles/global.css` | Design tokens and base styles |
| `.github/workflows/` | `update-data.yml` (cron), `deploy.yml` (Pages) |

## Commands
```bash
npm run dev        # local site at /ipo-update/
npm run check      # typecheck
npm run build      # static build to dist/
python3 scripts/validate.py
python3 -m unittest discover -s scripts/tests
```

## Hard rules
- Colours, radii and shadows come from tokens only.
- Only `src/lib/data.ts` reads `data/`. Internal links go through `url()`.
- Schema change = `docs/DATABASE.md` + `src/lib/data.ts` + `scripts/validate.py` together.
- No new dependency without asking. No secrets in the repo. No personal data.
- Scraper sources must be allowed by their robots.txt and terms.
- Never disable a failing test or loosen the validator to pass.
