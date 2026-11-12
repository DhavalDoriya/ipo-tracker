# Design system

Based on the "Google Material 3" design.md kit. Tokens live in `src/styles/global.css` as CSS custom properties. **Never hard-code a colour, radius or shadow; use a token.**

## Principles
1. Content first: numbers and dates are the interface; no decoration.
2. One accent: blue means "you can act on this".
3. Calm hierarchy: weight and size, not colour, separate levels.
4. Works without JavaScript; filters are an enhancement.

## Colour tokens
| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--color-bg` | `#ffffff` | `#131314` | Page background |
| `--color-surface` | `#f8f9fa` | `#1e1f20` | Cards, table header, inputs |
| `--color-border` | `#e1e3e1` | `#444746` | Dividers, input and card edges |
| `--color-text` | `#1f1f1f` | `#e3e3e3` | Body and headings |
| `--color-text-muted` | `#444746` | `#c4c7c5` | Labels, secondary text |
| `--color-primary` | `#0b57d0` | `#a8c7fa` | Buttons, active nav, focus ring |
| `--color-on-primary` | `#ffffff` | `#062e6f` | Text on primary |
| `--color-primary-container` / `--color-on-primary-container` | `#d3e3fd` / `#041e49` | `#0842a0` / `#d3e3fd` | Selected state: active nav, selected chip, tonal button, table header |
| `--color-link` | `#1a0dab` | `#a8c7fa` | Text links |
| `--color-success` / `-bg` | `#146c2e` / `#e6f4ea` | `#6dd58c` / `#0f5223` | Open, positive |
| `--color-warning` / `-bg` | `#8a5a00` / `#fef7e0` | `#fdd663` / `#5b4300` | Upcoming, caution |
| `--color-danger` / `-bg` | `#b3261e` / `#fce8e6` | `#f2b8b5` / `#601410` | Negative, errors |
| `--color-info` / `-bg` | `#0b57d0` / `#d3e3fd` | `#a8c7fa` / `#0842a0` | Listed status |
| `--color-surface-tint` | `#e8f0fe` | `#1a2639` | Home hero panel |
| `--tone-1..6-bg` / `-fg` | blue, red, yellow, green, purple, teal (100 / 900 shades) | same hues, dark container / light text | Company avatars only |

**Theme:** light and dark, chosen with the header toggle and saved in `localStorage` (`theme`). With no saved choice the system setting is used. `BaseLayout` sets `data-theme` on `<html>` before first paint; dark tokens live under `:root[data-theme='dark']`. Without JavaScript the site is light.

**Colour use:** colour always carries meaning. Status = green (open), amber (upcoming), blue (listed), grey (closed), on chips and filter dots. Gain = green / red. Avatar tones identify a company and mean nothing else. Never colour text or backgrounds for decoration.

The kit's border (`#f8f9fa`) is invisible on white, so a visible `#e1e3e1` is used. Semantic colours are added because the kit has none.

## Type
Roboto (self-hosted), fallback `Arial, sans-serif`.
| Token | Size / weight / line height | Use |
| --- | --- | --- |
| `--text-display` | 32px / 500 / 1.25 | Page title |
| `--text-heading` | 23px / 600 / 1.25 | Section title |
| `--text-title` | 16px / 600 / 1.5 | Card title |
| `--text-figure` | 18px / 500 / 1.25 | Key numbers on a card (price, subscription) |
| `--text-body` | 14px / 400 / 1.5 | Everything else |
| `--text-small` | 12px / 400 / 1.5 | Meta, chips |

## Spacing, radius, shadow, motion
- Spacing: `--space-1..6` = 4, 8, 12, 16, 20, 24px; `--space-section` = 48px (96px from 569px up).
- Radius: `--radius-sm` 8px (inputs, table), `--radius-md` 24px (cards), `--radius-pill` 9999px (buttons, chips).
- Shadow: `--shadow-card` = `rgba(60, 64, 67, 0.16) 0 2px 6px 0`.
- Motion: `--dur-fast` 50ms, `--dur-base` 250ms, `--dur-slow` 500ms, `--ease` `cubic-bezier(0.38, 0.72, 0, 1)`. All motion is off under `prefers-reduced-motion`.

## Motion
Little, and each piece has a job. Do not add entrance animations to sections or cards on load.
- **Page entrance** (one per page): the heading block (`.hero`, `.page-head`) rises 8px and fades in, its children 70ms apart.
- **Between pages**: a browser cross-fade (`@view-transition`); browsers without it just navigate.
- **Timeline**: the progress line draws from left to right the first time a card scrolls into view.
- **Response to an action**: cards lift 2px on hover; buttons press in; the menu sheet drops in; the theme icon turns in after a switch; cards brought back by search, a filter chip or "Show all" fade up.

## Components and states
Shared classes live in `global.css`: `.card`, `.btn`, `.btn-tonal`, `.rows`, `.actions`, `.grid`.

- **Header**: sticky single row with logo mark + name and the theme toggle. From 900px the pill nav sits in the bar. Below that a menu button opens a full-width sheet with every link as a 48px row; it closes on Escape or a tap outside, and works without JavaScript (`<details>`). Active page: primary-container + `aria-current`. Hover: surface. Active page: primary-container + `aria-current`. Focus: 2px primary outline.
- **Hero** (home only): surface panel, `--radius-md`, holding the page title, a one-line summary and the search. The search box is the one prominent element on the page.
- **Search + status chips** (`FilterBar`): pill search box, 52px, white on the panel; hover and focus lift it with `--shadow-card`. Chips are radio buttons with a status-coloured dot and a count: unselected = outlined, selected = primary-container. No result in a group shows "No IPOs here match your search."
- **Card** (`.card`; `IpoCard`, `BuybackCard`): outlined, `--radius-md`. Hover: shadow replaces the border. Rows without data are left out rather than shown as a dash.
- **Timeline** (`Timeline`): steps of a real sequence. A dot and its connecting line fill with primary once that step has happened. `IpoCard` uses Opens, Closes, Lists; `PipelineCard` uses Draft filed, Final filed, IPO dates.
- **Pipeline card** (`PipelineCard`): avatar, company, a stage chip ("Draft filed" outlined, "Final filed" amber), the filing timeline and a link to the filing.
- **Listing gain**: small pill after the listing price; success colours when up, danger when down, neutral at zero.
- **Status chip**: pill, 12px; open = success, upcoming = warning, listed = info, closed = neutral outline.
- **Avatar**: 40px circle with the company's initial; tone picked from the name so it is stable.
- **Theme toggle**: 44px icon button; shows a moon in light, a sun in dark; `aria-label` names the theme it switches to.
- **Footer**: link groups (Browse, Learn, Site) above the disclaimer and last-updated line.
- **Button** (`.btn`): filled primary pill, min height 44px; `.btn-tonal` uses primary-container. Hover: shadow. One filled button per view at most.
- **Rows** (`.rows`): bordered list for the checklist hub and guides. Hover: surface.
- **Show all**: long lists show the first few items with a tonal "Show all N" button; searching or filtering always looks through everything.
- **ChecklistTable**: column header on primary-container, section rows on surface; wrapped in a horizontally scrolling region with `tabindex="0"` and a label.
- **Empty state**: muted sentence in place of the list ("No IPOs are open for bidding today.").
- **Notice**: warning-bg block used for the GMP caution and sample-data banner.
- Loading and error states do not exist: pages are built ahead of time. A failed build never deploys.

## Breakpoints
Mobile first. `569px`: cards go from 1 column to an auto-fill grid, panels get more padding, footer goes from 2 to 3 columns. `900px`: header links move from the menu sheet into the bar.

## Accessibility
- Text contrast >= 4.5:1 in both themes; touch targets >= 44px.
- Visible focus on every interactive element; skip link to main content.
- One `h1` per page; tables use `th scope`.

## Copy tone
Plain, factual, short. Numbers with units (₹, x, shares). Never "should buy" or "recommended". Dates as `12 Nov 2026`.
