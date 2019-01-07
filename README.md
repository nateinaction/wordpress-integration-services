This docker image runs on a Kubernetes cron and is repsonsible for running automatic updates for the [WordPress Integration Docker Image](https://github.com/nateinaction/wordpress-integration/). When spun up, the image checks the current WordPress version in the integration docker and what's available from the WordPress API. If it detects an available update, the image will clone the repo, update the image, and publish to master.

When the updated Integration Docker image is published to master, a Travis CI job will build the image and verify it passes tests before pushing to Docker Hub.

The updator in `main.py` is a Github application and expects a private RSA key named `github_app_key.pem` to be mounted at `/github_app_key.pem`.
