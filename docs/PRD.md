# PRD: IPO Update

## Problem
Retail investors in India check several sites to find which IPOs are open, their price band, lot size and subscription, and have no structured way to judge an issue. Existing portals are ad-heavy and slow.

## Users
- **Retail investor**: wants today's IPOs, key dates and numbers on one fast page.
- **Learner**: wants a checklist that explains what to look at in an RHP and why.
- **Maintainer** (site owner): wants data to refresh without running a server.

## Goals (measurable)
- Pages load in under 2s on 3G; Lighthouse Performance and Accessibility >= 90.
- Data is at most 60 minutes old during market days, with the timestamp visible.
- Running cost is ₹0 (public GitHub repo, Actions, Pages).

## Non-goals (v1)
- Allotment status lookup, broker apply integration, user accounts, watchlists.
- Real-time subscription numbers. Automated GMP.
- Financial advice of any kind.

## Features
| Priority | Feature |
| --- | --- |
| P0 | IPO list (mainboard + SME) from `data/ipos.json` with last-updated time |
| P0 | Per-IPO analysis checklist (5 sections, 14 parameters) |
| P0 | Scheduled scraper that commits validated JSON only when data changed |
| P0 | Disclaimer and source attribution on every page |
| P0 | Automatic deploy to GitHub Pages |
| P1 | Buyback calendar |
| P1 | Client-side search and status filter |
| P1 | Guides (how to apply, KPIs explained), About page |
| P2 | GMP (manual entry), daily history archive, charts |

## User stories
**As an investor I see today's IPOs.**
- [ ] Home shows Open now, Coming soon and Recently listed sections from `data/ipos.json`.
- [ ] Each card shows name, exchange, dates, price band, lot size, subscription and status.
- [ ] `updated_at` is visible on the page.

**As an investor I filter the list.**
- [ ] Typing in search hides cards whose name does not match.
- [ ] Choosing a status shows only that status; an empty result shows an empty state.

**As a learner I read a checklist.**
- [ ] `/checklist/<slug>/` renders 5 sections and 14 parameters as Parameter | Meaning & Where to Find | Analysis.
- [ ] A GMP caution note is shown.
- [ ] On mobile the table scrolls horizontally and nothing else does.

**As the maintainer I get safe automatic updates.**
- [ ] `update-data.yml` runs on schedule and commits only when data changed.
- [ ] `validate.py` exits non-zero on malformed or empty data and nothing is committed.
- [ ] A data commit results in a new deploy.

**Compliance**
- [ ] Footer disclaimer on every page; sources listed on About.
- [ ] No secrets in the repo; no personal data collected.

## Flows
1. Home -> card -> source link (external) or checklist.
2. Home -> Mainboard / SME -> filter -> card.
3. Checklist hub -> checklist page.

## Screens
Home, Mainboard, SME, Buybacks, Checklist hub, Checklist detail, Guides (2), About.

## Open questions
- Which public source is allowed to be scraped (robots.txt and terms decide). Until settled the site ships sample data.
- Final GitHub repo name (sets the URL base path).
