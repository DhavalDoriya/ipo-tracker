# Testing

| What | With | Command |
| --- | --- | --- |
| Types and Astro templates | `astro check` | `npm run check` |
| Site builds from current data | Astro | `npm run build` |
| Data files match the schema | `scripts/validate.py` | `python3 scripts/validate.py` |
| Scraper helpers and validator | stdlib `unittest` | `python3 -m unittest discover -s scripts/tests` |
| Pages, filters, responsive, dark mode | Manual in a browser | `npm run preview` |

## Done means
- [ ] `npm run check` reports 0 errors.
- [ ] `npm run build` succeeds.
- [ ] `python3 scripts/validate.py` exits 0.
- [ ] `python3 -m unittest discover -s scripts/tests` passes.
- [ ] Changed pages looked at in the browser at mobile and desktop width, light and dark.
- [ ] Footer disclaimer still on every page.
- [ ] Docs updated if a decision changed.

Never disable a failing test or loosen the validator to get a green run.
