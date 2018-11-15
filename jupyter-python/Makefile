INTERACTIVE:=$(shell [ -t 0 ] && echo 1)
IMG=nephilimsolutions/jupiter-python
RUN=docker run -it --rm -v $(HOME)/.jupyter/$(PWD):/usr/local/lib/python3.6/site-packages -v $(PWD):/project -p 8888:8888 $(IMG)

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
