INTERACTIVE:=$(shell [ -t 0 ] && echo 1)
RUN=docker run --rm -v $(PWD):/project
IMG=docker-ci-python


help tests static-checks build connect repl clean build-docs reformat:
ifdef INTERACTIVE
	@$(RUN) -it $(IMG) $@
else
	@$(RUN) $(IMG) $@
endif

all: clean static-checks tests build build-docs


.PHONY: help build static-checks connect tests clean repl reformat all
.DEFAULT_GOAL: help
