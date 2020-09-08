# WordPress Integration Services

This docker image runs as a [Kubernetes cron job](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/). The image is repsonsible for running automatic updates for the [WordPress Integration Docker Image](https://github.com/nateinaction/wordpress-integration/). When spun up, the image checks the current WordPress version in the integration docker and what's available from the WordPress API. If it detects an available update, the image will clone the repo, update the image, and publish to master.

### Dependencies
- [docker](https://docs.docker.com/get-docker/)
- [gcloud](https://cloud.google.com/sdk/install)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [kustomize](https://kustomize.io)

#### Secrets
The updater in `main.py` is a Github application and expects a private RSA key named `github_app_key.pem` to be mounted at `/secrets/github_app_key.pem`. A [K8s secret](https://kubernetes.io/docs/concepts/configuration/secret/) can be created by running `kubectl create secret generic github-app-key-pem --from-file=./github_app_key.pem`.

### Developing
If you have a local cluster running you can create a hot reloading development environment by running `make build deploy`

### How to deploy
Build a tagged image, publish to the Google Container Registry and then updates the k8s cron spec.

```
gcloud auth login
gcloud components install kubectl
gcloud container clusters get-credentials gaia --zone us-central1-a --project api-in-k8s
gcloud auth configure-docker
make prod
kubectl get cronjobs
```
