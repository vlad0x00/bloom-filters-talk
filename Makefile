FIGURE_SRC := $(filter-out figures/style.py,$(wildcard figures/*.py))
FIGURE_STAMPS := $(patsubst figures/%.py,figures/out/.%.stamp,$(FIGURE_SRC))

.PHONY: all figures slides preview pdf clean

all: slides

figures: $(FIGURE_STAMPS)

figures/out/.%.stamp: figures/%.py figures/style.py
	@mkdir -p figures/out
	cd figures && uv run python $*.py
	@touch $@

slides: figures
	uv run quarto render

preview: figures
	uv run quarto preview

# Needs Chromium; prints the deck via reveal.js print mode.
pdf: slides
	npx --yes decktape reveal --size 1600x900 _site/index.html _site/slides.pdf

clean:
	rm -rf _site figures/out .quarto
