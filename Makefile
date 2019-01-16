.PHONY: test

IMAGE_NAME := worldpeaceio/wordpress-integration-services
UPDATE_DEVELOP_DIR := update_develop
MERGE_MASTER_DIR := merge_master
PYTHON_IMAGE := python
DOCKER_RUN := docker run --rm

all: build_image lint

build_image:
	docker build -t $(IMAGE_NAME) .

shell:
	$(DOCKER_RUN) -it -v `pwd`:/app -w /app --entrypoint "/bin/bash" $(IMAGE_NAME)

lint:
	$(DOCKER_RUN) --entrypoint "flake8" $(IMAGE_NAME) /workspace

test:
	$(DOCKER_RUN) -v `pwd`:/workspace --entrypoint "python" $(IMAGE_NAME) -m unittest discover /workspace/$(UPDATE_DEVELOP_DIR)
	$(DOCKER_RUN) -v `pwd`:/workspace --entrypoint "python" $(IMAGE_NAME) -m unittest discover /workspace/$(MERGE_MASTER_DIR)

test_run_update_develop:
	$(DOCKER_RUN) -v `pwd`/$(UPDATE_DEVELOP_DIR)/main.py:/$(UPDATE_DEVELOP_DIR)/main.py -v `pwd`/github_app_key.pem:/secrets/github_app_key.pem $(IMAGE_NAME) python /$(UPDATE_DEVELOP_DIR)/main.py

test_run_merge_master:
	$(DOCKER_RUN) -v `pwd`/$(MERGE_MASTER_DIR)/main.py:/$(MERGE_MASTER_DIR)/main.py -v `pwd`/github_app_key.pem:/secrets/github_app_key.pem $(IMAGE_NAME) python /$(MERGE_MASTER_DIR)/main.py