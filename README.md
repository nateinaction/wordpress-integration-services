# WordPress Integration Services

This docker image runs as a [Kubernetes cron job](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/). The image is repsonsible for running automatic updates for the [WordPress Integration Docker Image](https://github.com/nateinaction/wordpress-integration/). When spun up, the image checks the current WordPress version in the integration docker and what's available from the WordPress API. If it detects an available update, the image will clone the repo, update the image, and publish to master.

### Dependencies
- [docker](https://docs.docker.com/get-docker/)
- [gcloud](https://cloud.google.com/sdk/install)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [kustomize](https://kubernetes-sigs.github.io/kustomize/installation/)

### Developing
If you have a local cluster running you can create a hot reloading development environment by running `make deploy`

You can clean up your local environment by running `make tear_down`

### How to deploy
~~Just merge to master. Google Cloud Build handles building and tagging the image, publishing it to the Google Container Registry and then deploying an updated spec to the cluster.~~

Currently, this needs to be deployed by hand because we've moved to a cluster with a private master which Cloudbuild does not have access to.
```
gcloud auth login
gcloud components install kubectl
gcloud container clusters get-credentials royal-brook --zone us-central1-a --project worldpeaceio-production
# Update the master authorized networks for the k8s cluster to include your IP
KUBECTX="gke_worldpeaceio-production_us-central1-a_royal-brook" make deploy
```

### How to check on the status of a deploy
```
gcloud auth login
gcloud components install kubectl
gcloud container clusters get-credentials royal-brook --zone us-central1-a --project worldpeaceio-production
# Update the master authorized networks for the k8s cluster to include your IP
kubectl get cronjobs
```
