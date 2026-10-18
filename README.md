# Sangam Europa

Website of Sangam Europa, a quarterly magazine on relations between India and Europe, edited in Berlin: https://sangam-europa.com

## How the site is built

The site is static HTML and CSS with no framework and no tracking. `build.py` holds the content and generates every page into `public/`, which is the only folder that is published.

```
build.py                       content and page generator
public/                        the published website
  assets/                      styles, logos and self-hosted fonts (SIL Open Font License)
  data/                        data behind the charts, as a downloadable CSV
.github/workflows/pages.yml    publishes public/ to GitHub Pages on every push to main
```

**To change the site:** edit `build.py`, run `python3 build.py` (Python 3.9 or newer, standard library only), then commit and push. The site updates a minute or two later.

**To preview locally:** run `cd public && python3 -m http.server 8000` and open http://localhost:8000.

## Sources

Every fact on the site links to its source, and each page lists its sources at the bottom. The figures were last checked on 17 October 2026.

## Contact

tony@sangam-europa.com
