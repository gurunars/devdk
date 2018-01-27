INTERACTIVE:=$(shell [ -t 0 ] && echo 1)
RUN=docker run --rm -v $(PWD):/project
IMG=docker-ci-python


help validate tests style-checks build connect repl:
ifdef INTERACTIVE
	@$(RUN) -it $(IMG) $@
else
	@$(RUN) $(IMG) $@
endif

clean:
	-@docker rmi -f $(IMG) > /dev/null 2>&1 | true


.PHONY: help validate build style-checks connect tests image clean repl
.DEFAULT_GOAL: help
