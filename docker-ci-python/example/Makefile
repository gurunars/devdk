INTERACTIVE:=$(shell [ -t 0 ] && echo 1)
RUN=docker run --rm -v $(PWD):/project
IMG=docker-ci-python


help validate build connect repl clean reformat:
ifdef INTERACTIVE
	@$(RUN) -it $(IMG) $@
else
	@$(RUN) $(IMG) $@
endif

all: clean validate build


.PHONY: help validate build connect clean repl reformat
.DEFAULT_GOAL: help
