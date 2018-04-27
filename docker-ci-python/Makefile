INTERACTIVE:=$(shell [ -t 0 ] && echo 1)
RUN=docker run --rm -v $(PWD):/project
IMG=nephilimsolutions/docker-ci-python

all: clean static-checks tests

image:
	@docker build . -t $(IMG)

help static-checks tests connect repl reformat: image
ifdef INTERACTIVE
	@$(RUN) -it $(IMG) $@
else
	@$(RUN) $(IMG) $@
endif

clean:
	-@$(RUN) $(IMG) clean > /dev/null 2>&1 | true
	-@docker rmi -f $(IMG) > /dev/null 2>&1 | true

.PHONY: help static-checks connect tests image clean repl reformat all
.DEFAULT_GOAL: help
