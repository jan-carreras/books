#!/usr/bin/env make

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


generate: books/content books/public ## Generate posts and site

clean-generated:
	rm -f books/content/*.md

books/content: clean-generated
	python3 parse.py

clean-public:
	rm -rf books/public
	mkdir -p books/public

books/public: clean-public
	hugo -s books

.PHONY: clean-generated clean-public generate
