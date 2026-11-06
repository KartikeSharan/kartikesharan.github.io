# kartikesharan.github.io

Source for my portfolio site: <https://kartikesharan.github.io>. The design files and code it links to are in [engineering-projects](https://github.com/KartikeSharan/engineering-projects).

The site is styled as a printed circuit board, and the solder mask colour can be changed at the bottom of each page.

## How it's built

Plain HTML, CSS and a little JavaScript, served by GitHub Pages with no build step on GitHub's side (`.nojekyll` turns Jekyll off).

| Path | What it is |
|---|---|
| `index.html`, `projects/*.html`, `404.html`, `sitemap.xml` | Generated pages: edit `tools/build.py`, not these |
| `tools/build.py` | All the page text and layout. Run `python3 tools/build.py` from the repo root after any change |
| `tools/wave.py` | Draws the RISC16 timing diagram from a testbench VCD dump |
| `tools/tcad_plot.py` | Draws the TCAD current-voltage chart from the Sentaurus `.plt` output |
| `assets/css/site.css` | Colours (one block per solder mask), type and layout |
| `assets/js/site.js` | Solder mask picker, the traces on the home page, the copper layer viewer |
| `assets/img/` | Board renders made from my Gerber files, plus figures from my lab reports |
| `assets/fig/` | SVG figures whose colours follow the chosen solder mask |
| `assets/fonts/` | B612 and Atkinson Hyperlegible, both under the SIL Open Font License |

To preview locally: `python3 -m http.server` in the repo root, then open <http://localhost:8000>.
