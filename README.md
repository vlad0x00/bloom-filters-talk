# Bloom filters talk

Slides for a ~30-minute talk on Bloom filters and their variants at [Vancouver Systems](https://vancouver.systems).

## Stack

- **Slides:** [Quarto](https://quarto.org) → reveal.js (HTML). Content lives in `index.qmd` (Markdown, KaTeX math, speaker notes).
- **Figures and animations:** Python scripts in `figures/`, run with [uv](https://docs.astral.sh/uv/). Static plots are SVG; animations are MP4 (matplotlib + ffmpeg). Output goes to `figures/out/` (not committed).
- **Publishing:** GitHub Actions renders the deck and deploys it to GitHub Pages on every push to `main`.

## Requirements

`uv`, `quarto`, `ffmpeg`, `make`. For PDF export: Node.js (uses `decktape`).

## Usage

```sh
make figures   # regenerate changed figures only
make preview   # live-reloading preview in the browser
make slides    # render to _site/index.html
make pdf       # export _site/slides.pdf
```

Presenter view: press `S` in the browser. Overview: `O`.

## Adding a figure

Create `figures/<name>.py` that writes to `OUT / "<name>.svg"` (or `.mp4`), importing paths and style from `figures/style.py`. Reference it in `index.qmd` as `figures/out/<name>.svg` or `{{< video figures/out/<name>.mp4 >}}`.
