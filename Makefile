LOCAL_CTX := docker-for-desktop
PROD_CTX := gke_api-in-k8s_us-central1-a_gaia
PROD_IMAGE_REGISTRY := us.gcr.io/api-in-k8s/

IMAGE_NAME := wordpress-integration-services
INITIAL_TAG := $(shell date | shasum -a 256 | cut -d' ' -f1)
IMAGE_TAG = $(shell docker images $(IMAGE_NAME):$(INITIAL_TAG) --format '{{.ID}}')

ARTIFACTS_DIR := artifacts

.PHONY: all
all: build

.PHONY: docker_build
docker_build:
	docker build -t $(IMAGE_NAME):$(INITIAL_TAG) .

docker_tag:
	docker tag $(IMAGE_NAME):$(INITIAL_TAG) $(IMAGE_REGISTRY)$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: build
build: docker_build docker_tag
	rm -rf $(ARTIFACTS_DIR)
	mkdir -p $(ARTIFACTS_DIR)
	cd $(ARTIFACTS_DIR) && kustomize create --resources ../deploy --labels app:wordpress-integration-services
	cd $(ARTIFACTS_DIR) && kustomize edit set image $(IMAGE_NAME)=$(IMAGE_REGISTRY)$(IMAGE_NAME) $(IMAGE_REGISTRY)$(IMAGE_NAME)=$(IMAGE_REGISTRY)$(IMAGE_NAME):$(IMAGE_TAG)
	cd $(ARTIFACTS_DIR) && kustomize build . > $(IMAGE_NAME).yaml

.PHONY: docker_push
docker_push:
	docker push $(IMAGE_REGISTRY)$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: deploy
deploy:
	kubectx $(LOCAL_CTX)
	kubectl apply -f $(ARTIFACTS_DIR)/$(IMAGE_NAME).yaml

.PHONY: tear_down
tear_down:
	kubectx $(LOCAL_CTX)
	kubectl delete -f $(ARTIFACTS_DIR)/$(IMAGE_NAME).yaml

# Prod
.PHONY: prod
prod: IMAGE_REGISTRY=$(PROD_IMAGE_REGISTRY)
prod: build docker_push deploy_prod

.PHONY: deploy_prod
deploy_prod:
	kubectx $(PROD_CTX)
	kubectl apply -f $(ARTIFACTS_DIR)/$(IMAGE_NAME).yaml
