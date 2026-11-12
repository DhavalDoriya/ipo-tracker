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
| `--color-link` | `#1a0dab` | `#a8c7fa` | Text links |
| `--color-success` / `-bg` | `#146c2e` / `#e6f4ea` | `#6dd58c` / `#0f5223` | Open, positive |
| `--color-warning` / `-bg` | `#8a5a00` / `#fef7e0` | `#fdd663` / `#5b4300` | Upcoming, caution |
| `--color-danger` / `-bg` | `#b3261e` / `#fce8e6` | `#f2b8b5` / `#601410` | Negative, errors |

The kit's border (`#f8f9fa`) is invisible on white, so a visible `#e1e3e1` is used. Semantic colours are added because the kit has none.

## Type
Roboto (self-hosted), fallback `Arial, sans-serif`.
| Token | Size / weight / line height | Use |
| --- | --- | --- |
| `--text-display` | 32px / 500 / 1.25 | Page title |
| `--text-heading` | 23px / 600 / 1.25 | Section title |
| `--text-title` | 16px / 600 / 1.5 | Card title |
| `--text-body` | 14px / 400 / 1.5 | Everything else |
| `--text-small` | 12px / 400 / 1.5 | Meta, chips |

## Spacing, radius, shadow, motion
- Spacing: `--space-1..6` = 4, 8, 12, 16, 20, 24px; `--space-section` = 48px (96px from 569px up).
- Radius: `--radius-sm` 8px (inputs, table), `--radius-md` 24px (cards), `--radius-pill` 9999px (buttons, chips).
- Shadow: `--shadow-card` = `rgba(60, 64, 67, 0.16) 0 2px 6px 0`.
- Motion: `--dur-fast` 50ms, `--dur-base` 250ms, `--ease` `cubic-bezier(0.38, 0.72, 0, 1)`. All transitions off under `prefers-reduced-motion`.

## Components and states
- **Button / nav link**: pill, min height 44px. Hover: surface tint. Focus: 2px primary outline, 2px offset. Active page: primary text + `aria-current`.
- **Card** (`IpoCard`, `BuybackCard`): surface background, `--radius-md`, shadow on hover only. Missing values render as "—".
- **Status chip**: pill, 12px; open = success, upcoming = warning, closed / listed = neutral.
- **FilterBar**: search input + status select, 44px tall. Empty result shows "No IPOs match your filter."
- **ChecklistTable**: header row on surface; wrapped in a horizontally scrolling region with `tabindex="0"` and a label.
- **Empty state**: muted sentence in place of the list ("No IPOs open right now.").
- **Notice**: warning-bg block used for the GMP caution and sample-data banner.
- Loading and error states do not exist: pages are built ahead of time. A failed build never deploys.

## Breakpoints
Mobile first; one breakpoint at `569px` (cards go from 1 column to an auto-fill grid, nav from scroll row to inline).

## Accessibility
- Text contrast >= 4.5:1 in both themes; touch targets >= 44px.
- Visible focus on every interactive element; skip link to main content.
- One `h1` per page; tables use `th scope`.

## Copy tone
Plain, factual, short. Numbers with units (₹, x, shares). Never "should buy" or "recommended". Dates as `12 Nov 2026`.
