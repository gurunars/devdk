INTERACTIVE:=$(shell [ -t 0 ] && echo 1)
RUN=docker run --rm -v $(PWD):/project
IMG=docker-ci-python


help validate tests style-checks build connect repl clean reformat:
ifdef INTERACTIVE
	@$(RUN) -it $(IMG) $@
else
	@$(RUN) $(IMG) $@
endif


.PHONY: help validate build style-checks connect tests image clean repl reformat
.DEFAULT_GOAL: help
