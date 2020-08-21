.PHONY: all
all: build

.PHONY: build
build:
	skaffold build

.PHONY: dev
dev:
	skaffold dev --no-prune=false -p local

.PHONY: deploy
deploy:
	skaffold run -p prod
