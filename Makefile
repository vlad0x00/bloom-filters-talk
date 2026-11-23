FIGURE_SRC := $(filter-out figures/style.py figures/hashing.py,$(wildcard figures/*.py))
FIGURE_STAMPS := $(patsubst figures/%.py,figures/out/.%.stamp,$(FIGURE_SRC))

.PHONY: all figures slides preview serve pdf clean

all: slides

figures: $(FIGURE_STAMPS)

figures/out/.%.stamp: figures/%.py figures/style.py figures/hashing.py
	@mkdir -p figures/out
	cd figures && uv run python $*.py
	@touch $@

slides: figures
	uv run quarto render

preview: figures
	uv run quarto preview

# Serve the built deck over HTTP (speaker notes don't sync over file://).
serve: slides
	@echo "Open http://localhost:8000"
	cd _site && python3 -m http.server 8000

# Needs Chromium; prints the deck via reveal.js print mode.
pdf: slides
	npx --yes decktape reveal --size 1600x900 _site/index.html _site/slides.pdf

clean:
	rm -rf _site figures/out .quarto
