INTERACTIVE:=$(shell [ -t 0 ] && echo 1)
RUN=docker run -it -u=$(UID):$(id -g $USER) --rm -v $(PWD):/project -p 8888:8888 $(IMG)
IMG=nephilimsolutions/jupiter-kotlin

all: clean image

image:
	@docker build . -t $(IMG)

run:
	@$(RUN)

ssh:
	@$(RUN) ssh

clean:
	-@docker rmi -f $(IMG) > /dev/null 2>&1 | true

.PHONY: image all run clean ssh
.DEFAULT_GOAL: run
