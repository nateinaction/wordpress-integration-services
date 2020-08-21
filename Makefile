.PHONY: all
all: build

.PHONY: build
build:
	skaffold build

.PHONY: dev
dev:
	skaffold dev

.PHONY: deploy
deploy:
	skaffold run
