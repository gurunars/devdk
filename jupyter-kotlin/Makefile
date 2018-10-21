INTERACTIVE:=$(shell [ -t 0 ] && echo 1)
IMG=nephilimsolutions/jupiter-kotlin
RUN=docker run -it --rm -v $(HOME)/.jupyter/$(PWD):/home/jupyter/.m2 -v $(PWD):/project -p 8888:8888 $(IMG)

all: clean image

image:
	docker build . -t $(IMG)

start:
	$(RUN)

ssh:
	$(RUN) ssh

clean:
	-rm -rf $(HOME)/.jupyter/$(PWD)
	-docker rmi -f $(IMG) > /dev/null 2>&1 | true

.PHONY: image all start clean ssh
.DEFAULT_GOAL: run
