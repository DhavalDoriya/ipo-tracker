# Data

There is no database. The data store is JSON files in `data/`, versioned by git. TypeScript types in `src/lib/data.ts` and the checks in `scripts/validate.py` are the schema; keep the three in step.

## Conventions
- `snake_case` keys. Dates are `YYYY-MM-DD`; timestamps are ISO 8601 UTC.
- `id` is a lowercase kebab-case slug, unique within its file, stable over time.
- Unknown values are `null`, never `""` or `"N/A"`.
- Money is a number in rupees. Subscription is a string such as `"12.85x"`.

## Files
| File | Written by | Purpose |
| --- | --- | --- |
| `ipos.json` | scraper | Current and recent IPOs, mainboard + SME |
| `coming_soon.json` | scraper (SEBI filings) | IPOs in the pipeline: offer document filed, no dates yet |
| `buybacks.json` | hand | Buyback calendar; `sample: true` shows a placeholder banner |
| `gmp.json` | hand | Unofficial grey market premium, joined to IPOs by `id` |
| `checklists/<slug>.json` | hand | One analysis checklist per IPO |
| `history/<date>.json` | scraper | Daily copy of `ipos.json` |

## `ipos.json`
Top level: `updated_at`, `source`, optional `sample` (true while data is placeholder), `ipos[]`.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | required |
| `name` | string | required |
| `type` | `"mainboard"` \| `"sme"` | required |
| `exchange` | string \| null | e.g. `"NSE, BSE"`, `"BSE SME"`; null when the source does not say |
| `status` | `"upcoming"` \| `"open"` \| `"closed"` \| `"listed"` | required |
| `open_date`, `close_date`, `listing_date` | date \| null | |
| `offer_price` | `{ min, max }` \| null | rupees |
| `list_price` | number \| null | |
| `lot_size` | number \| null | shares |
| `issue_size` | string \| null | e.g. `"₹120.5 Cr"` |
| `subscription` | string \| null | overall |
| `subscription_breakup` | `{ retail, hni, qib }` \| null | |
| `gmp` | number \| null | normally null; see `gmp.json` |
| `source_url` | string \| null | |

## `coming_soon.json`
`updated_at`, `source`, `ipos[]` of `{ id, name, type, exchange, expected, source_url }`. `exchange` may be null. `expected` is free text: an expected month, or the latest filing (`"RHP filing, 26 Oct 2026"`). The scraper rewrites this file from the `filings` entries in `scripts/sources.json`; one entry per company, RHP stage first.

## `buybacks.json`
`updated_at`, `buybacks[]` of `{ id, name, type ("tender" | "open_market"), record_date, open_date, close_date, buyback_price, status ("upcoming" | "open" | "closed") }`.

## `gmp.json`
`updated_at`, `note`, `entries[]` of `{ id, gmp, percent }`.

## `checklists/<slug>.json`
`company`, optional `ipo_id`, `sections[]` of `{ title, parameters[] }`; each parameter is `{ name, meaning, positive, negative, analysis }`. The file name is the URL slug.

## Access rules
Everything in `data/` is public. Never put personal data, PAN numbers or credentials here.

## Changing the schema
1. Update this doc, `src/lib/data.ts` types and `scripts/validate.py` in one change.
2. Update the sample files so the build and validator pass.

## Deletion
IPOs drop out of `ipos.json` when the source no longer lists them; they remain in `history/` and git history.
