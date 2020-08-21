# WordPress Integration Services

This docker image runs as a Kubernetes cron job. The image is repsonsible for running automatic updates for the [WordPress Integration Docker Image](https://github.com/nateinaction/wordpress-integration/). When spun up, the image checks the current WordPress version in the integration docker and what's available from the WordPress API. If it detects an available update, the image will clone the repo, update the image, and publish to master.

The updater in `main.py` is a Github application and expects a private RSA key named `github_app_key.pem` to be mounted at `/secrets/github_app_key.pem`. A K8s secret can be created by running `kubectl create secret generic github-app-key-pem --from-file=./github_app_key.pem`: https://kubernetes.io/docs/concepts/configuration/secret/

### How to deploy

#### Changes to the docker image
The docker image is built and published by Docker Hub's CI pipeline on merge to master. The next time the k8s cron runs it will pull the latest image from Docker Hub.

#### Changes to the k8s cron spec
To apply a new cron spec:
```
gcloud auth login
gcloud components install kubectl
gcloud container clusters get-credentials gaia --zone us-central1-a --project api-in-k8s
kubectl apply -f .
kubectl get cronjob
```
