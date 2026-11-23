# Bloom filters talk

Slides for a ~30-minute talk on Bloom filters and their variants at [Vancouver Systems](https://vancouver.systems).

## Stack

- **Slides:** [Quarto](https://quarto.org) → reveal.js (HTML). Quarto is a project dev dependency (`quarto-cli` in `pyproject.toml`), run via `uv run quarto`. Content lives in `index.qmd` (Markdown, KaTeX math, speaker notes).
- **Figures and animations:** Python scripts in `figures/`, run with [uv](https://docs.astral.sh/uv/). Static plots are SVG; animations are WebM with a transparent background (matplotlib + ffmpeg, VP9). Output goes to `figures/out/` (not committed).

## Requirements

`uv`, `ffmpeg`, `make`. uv installs everything else (including Quarto) into `.venv` on first run. For PDF export: Node.js (uses `decktape`).

## Usage

```sh
make figures   # regenerate changed figures only
make preview   # live-reloading preview in the browser
make slides    # render to _site/index.html
make serve     # build, then serve at http://localhost:8000 (use this to present)
make pdf       # export _site/slides.pdf
```

Presenter view: press `S` in the browser. Open the deck over HTTP (`make serve` or `make preview`), not as a `file://` path: over `file://` the speaker notes stay empty. Overview: `O`.

## Adding a figure

Create `figures/<name>.py` that writes to `OUT / "<name>.svg"` (for animations, call `save_animation(anim, "<name>", fps)`), importing paths and style from `figures/style.py`. Reference it in `index.qmd` as `figures/out/<name>.svg` or `<video data-autoplay muted playsinline src="figures/out/<name>.webm"></video>`.
