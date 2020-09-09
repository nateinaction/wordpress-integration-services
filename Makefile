IMAGE_NAME := wordpress-integration-services
INITIAL_TAG := $(shell date | sha256sum | head -c 8)
IMAGE_TAG = $(shell docker images $(IMAGE_NAME):$(INITIAL_TAG) --format '{{.ID}}')

ARTIFACTS_DIR := artifacts
LOCAL_K8S_CTX := docker-for-desktop
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

.PHONY: deploy
deploy:
	kubectx $(LOCAL_K8S_CTX)
	kubectl apply -f $(K8S_CONFIG)

.PHONY: tear_down
tear_down:
	kubectx $(LOCAL_K8S_CTX)
	kubectl delete -f $(K8S_CONFIG)
