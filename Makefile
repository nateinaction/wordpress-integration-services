.PHONY: test

UPDATE_DEVELOP_IMAGE := worldpeaceio/wordpress-integration-update-develop
UPDATE_DEVELOP_DIR := update_develop
MERGE_MASTER_IMAGE := worldpeaceio/wordpress-integration-merge-master
MERGE_MASTER_DIR := merge_master
PYTHON_IMAGE := python
DOCKER_RUN := docker run --rm

all: build_images lint

build_images:
	docker build -t $(UPDATE_DEVELOP_IMAGE) $(UPDATE_DEVELOP_DIR)
	docker build -t $(MERGE_MASTER_IMAGE) $(MERGE_MASTER_DIR)

shell:
	$(DOCKER_RUN) -it -v `pwd`:/app -w /app --entrypoint "/bin/bash" $(UPDATE_DEVELOP_IMAGE)

lint:
	$(DOCKER_RUN) --entrypoint "flake8" $(UPDATE_DEVELOP_IMAGE) /workspace

test:
	$(DOCKER_RUN) -v `pwd`:/workspace --entrypoint "python" $(UPDATE_DEVELOP_IMAGE) -m unittest discover /workspace/$(UPDATE_DEVELOP_DIR)
	$(DOCKER_RUN) -v `pwd`:/workspace --entrypoint "python" $(MERGE_MASTER_IMAGE) -m unittest discover /workspace/$(MERGE_MASTER_DIR)

test_run_update_develop:
	$(DOCKER_RUN) -v `pwd`/$(UPDATE_DEVELOP_DIR)/main.py:/main.py -v `pwd`/github_app_key.pem:/secrets/github_app_key.pem $(UPDATE_DEVELOP_IMAGE)

test_run_merge_master:
	$(DOCKER_RUN) -v `pwd`/$(MERGE_MASTER_DIR)/main.py:/main.py -v `pwd`/github_app_key.pem:/secrets/github_app_key.pem $(MERGE_MASTER_IMAGE)