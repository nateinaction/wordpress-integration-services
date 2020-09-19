IMAGE := wordpress-integration-services
REGISTRY := us.gcr.io/worldpeace-container-registry/
INITIAL_TAG := $(shell date | sha256sum | head -c 8)
FINAL_TAG = $(shell docker images $(IMAGE):$(INITIAL_TAG) --format '{{.ID}}')
KUBE_CTX ?= docker-for-desktop

.PHONY: all
all: kustomization.yaml

artifacts:
	mkdir artifacts

artifacts/initial_image.txt: artifacts
	docker build -t $(IMAGE):$(INITIAL_TAG) .
	echo $(REGISTRY)$(IMAGE):$(INITIAL_TAG) > artifacts/initial_image.txt

artifacts/image.txt: artifacts/initial_image.txt
	docker tag $(IMAGE):$(INITIAL_TAG) $(REGISTRY)$(IMAGE):$(FINAL_TAG)
	echo $(REGISTRY)$(IMAGE):$(FINAL_TAG) > artifacts/image.txt

artifacts/wordpress-integration-services.yaml: artifacts/image.txt
	kubectl set image -f config $(IMAGE)=$(shell cat artifacts/image.txt) --local -o yaml > artifacts/wordpress-integration-services.yaml

github_app_key.pem:
	mkdir -p secrets/
	gcloud secrets versions access latest --secret=wordpress-integration-services-github-app-key > github_app_key.pem

kustomization.yaml: artifacts/wordpress-integration-services.yaml github_app_key.pem
	rm -f kustomization.yaml
	kustomize create --resources artifacts/wordpress-integration-services.yaml
	kustomize edit add secret github-app-key-pem --from-file=github_app_key.pem

.PHONY: docker_push
docker_push: artifacts/image.txt
	docker push $(shell cat artifacts/image.txt)

.PHONY: deploy
deploy: kustomization.yaml
	kubectx $(KUBECTX)
	kubectl apply -k .

.PHONY: tear_down
tear_down: kustomization.yaml
	kubectx $(KUBECTX)
	kubectl delete -k .

.PHONY: clean
clean:
	rm -rf artifacts
	rm -f github_app_key.pem
	rm -f kustomization.yaml
