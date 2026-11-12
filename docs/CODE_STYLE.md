# Code style

Only rules a linter cannot enforce.

## Naming
- Components: `PascalCase.astro`. Pages and lib files: `kebab-case`.
- JSON keys and Python: `snake_case`. TypeScript variables and functions: `camelCase`; the data types keep the JSON's `snake_case` fields.
- CSS classes: short, component-scoped (`.card`, `.chip`). Tokens: `--color-*`, `--space-*`, `--radius-*`, `--text-*`.

## Size
- A component over ~120 lines or a function over ~40 lines should be split.
- One component per file.

## Patterns to use
- Scoped `<style>` in each component; tokens, base rules and the few shared classes (`.card`, `.btn`, `.rows`) only in `global.css`.
- Pass data to components as typed props.
- Format every date and amount through `src/lib/format.ts`.
- Build every internal link with `url()` from `src/lib/url.ts`.
- In Python, one parser function per source returning a list of dicts in the `ipos.json` shape.

## Patterns to avoid
- Hard-coded colours, radii or shadows (breaks dark mode and the design system).
- Reading `data/` outside `src/lib/data.ts` (one place to change when the schema changes).
- `set:html` or `innerHTML` with data (injection).
- Client-side frameworks or fetches (the site is static by design).
- Catch-all `except: pass` in the scraper (hides a broken source).

## Error handling
- Build: a missing or malformed data file throws and fails the build. Never deploy a half-empty site.
- Missing optional values render as "—" via the format helpers.
- Scraper: a failing source logs a warning and is skipped; if no source returns data the script exits 1 and existing data is left as is.
