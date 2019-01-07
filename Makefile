IMAGE_NAME := nateinaction/wordpress-integration-updater
DOCKER_RUN := docker run --rm

all: build_docker lint

build_docker:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

shell:
	$(DOCKER_RUN) -it -v `pwd`:/app -w /app --entrypoint "/bin/bash" $(IMAGE_NAME)

lint:
	$(DOCKER_RUN) -it --entrypoint "flake8" $(IMAGE_NAME) /workspace

publish:
	docker push $(IMAGE_NAME)

test_run:
	$(DOCKER_RUN) -v `pwd`/main.py:/main.py -v `pwd`/github_app_key.pem:/github_app_key.pem $(IMAGE_NAME)