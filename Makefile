K8S_CTX ?= docker-for-desktop
PROD_CTX := gke_api-in-k8s_us-central1-a_gaia
PROD_IMAGE_REGISTRY := us.gcr.io/api-in-k8s/

IMAGE_NAME := wordpress-integration-services
INITIAL_TAG := $(shell date | shasum -a 256 | cut -d' ' -f1)
IMAGE_TAG = $(shell docker images $(IMAGE_NAME):$(INITIAL_TAG) --format '{{.ID}}')

ARTIFACTS_DIR := artifacts
K8S_CONFIG := $(ARTIFACTS_DIR)/$(IMAGE_NAME).yaml
CLOUD_BUILD_PKG := $(ARTIFACTS_DIR)/$(IMAGE_NAME).tar.gz

.PHONY: build
build: docker k8s_config

.PHONY: docker
docker: docker_build docker_tag

.PHONY: docker_build
docker_build:
	docker build -t $(IMAGE_NAME):$(INITIAL_TAG) .

.PHONY: docker_tag
docker_tag:
	docker tag $(IMAGE_NAME):$(INITIAL_TAG) $(IMAGE_REGISTRY)$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: docker_push
docker_push:
	docker push $(IMAGE_REGISTRY)$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: mkdir
mkdir:
	mkdir -p $(ARTIFACTS_DIR)

.PHONY: k8s_config
k8s_config: mkdir
	kubectl set image -f deploy $(IMAGE_NAME)=$(IMAGE_REGISTRY)$(IMAGE_NAME):$(IMAGE_TAG) --local -o yaml > $(K8S_CONFIG)

.PHONY: cloud_build
cloud_build:
	tar -czvf $(CLOUD_BUILD_PKG) $(K8S_CONFIG)
	gcloud builds submit $(CLOUD_BUILD_PKG)

.PHONY: deploy
deploy:
	kubectx $(K8S_CTX)
	kubectl apply -f $(K8S_CONFIG)

.PHONY: tear_down
tear_down:
	kubectx $(K8S_CTX)
	kubectl delete -f $(K8S_CONFIG)

# Prod
.PHONY: prod
prod: K8S_CTX=$(PROD_CTX)
prod: IMAGE_REGISTRY=$(PROD_IMAGE_REGISTRY)
prod: build docker_push cloud_build
