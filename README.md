# Fortune Cookies practice with Kubernetes and Helm

1. [Some initial setup](#some-initial-setup)
   1. [Requirements](#requirements)
   2. [Local cluster creation with Kind](#local-cluster-creation-with-kind)
   3. [Build and load of local images](#build-and-load-of-local-images)
2. [The practice](#the-practice)
   1. [STEP 1 - Create a Helm chart](#step-1---create-a-helm-chart)
   2. [STEP 2 - Use a redis chart as dependency of our fortune-cookies chart](#step-2---use-a-redis-chart-as-dependency-of-our-fortune-cookies-chart)
   3. [STEP 3 - Set up a cronjob that reads fortune cookies from Redis and outputs it to stdout](#step-3---set-up-a-cronjob-that-reads-fortune-cookies-from-redis-and-outputs-them-to-stdout)
   4. [STEP 4 - STEP 4 - Set up a cronjob that queues up fortune cookies to Redis](#step-4---set-up-a-cronjob-that-queues-up-fortune-cookies-to-redis)
   5. [STEP 5 - Make an accessible endpoint that reads fortune cookies from Redis and returns them as response](#step-5---make-an-accessible-endpoint-that-reads-fortune-cookies-from-redis-and-returns-them-as-response)

## Some initial setup

### Requirements
- docker (or docker desktop)
- kubectl
- kind (or minikube or k3d if you feel brave)
- helm

Is quite possible that brew, macports or your distro package manager installs most of the requirements just by installing kind.

### Local cluster creation with Kind

```shell
kind create cluster --name devel --kubeconfig ~/.kube/devel-config
kind export kubeconfig --name devel
```

Feel free to replace `~/.kube/devel-config` with whatever path you prefer.
The `--kubeconfig` must be included to prevent kind from messing up any default k8s configuration you have.

From now on, on every `kind` command you use, you'll need to include `--name devel`, which is the name of the cluster.

The `export` command make the `devel` kubeconfig the default one in your current terminal. If not exported or if you change your terminal, then you'll need to add `--kubeconfig ~/.kube/devel-config` to almost all your helm command calls.

### Build and load of local images

We need to build and load our custom docker images to kind in order to avoid using a docker registry.

Kind (k3d too, I don't know if minikube does) has a mechanism to tell the local cluster to use a locally generated image instead of trying to get it from a docker registry.

```shell
docker build \
  --target fortune-cookies-takeaway-customer \
  --tag fortune-cookie-takeaway:latest \
  -f docker/fortune-cookies/Dockerfile \
  docker/fortune-cookies/

kind load docker-image --name devel fortune-cookies-takeaway:latest

docker build \
  --target fortune-cookies-delivery-customer \
  --tag fortune-cookie-delivery:latest \
  -f docker/fortune-cookies/Dockerfile \
  docker/fortune-cookies/

kind load docker-image --name devel fortune-cookies-delivery:latest

docker build \
  --target fortune-cookies-chef \
  --tag fortune-cookies-chef:latest \
  -f docker/fortune-cookies/Dockerfile \
  docker/fortune-cookies/

kind load docker-image --name devel fortune-cookies-chef:latest
```


## The practice

### STEP 1 - Create a Helm chart

```shell
helm create helm-charts/fortune-cookies
```

Have a look to the resulting files in `helm-charts/fortune-cookies`.
Can you make any sense of the templating engine and the values?

## STEP 2 - Use a redis chart as dependency of our fortune-cookies chart

The idea is to end up this practice step with a running redis instance in our cluster.

In order to do that, add the next YAML to the `Chart.yaml` file on your recently created chart (or get the help of your Jetbrains IDE to add the dependency from bitnami's repo):
```yaml
dependencies:
  - name: redis
    version: 17.13.2
    repository: https://charts.bitnami.com/bitnami
```

Build the newly declared dependency and intall our chart in the k8s cluster
```shell
helm dependency build helm-charts/fortune-cookies/
helm install fortuneCookies helm-charts/fortune-cookies/
```

Review available config values for that redis dependency and think about what you can tweak with them: https://artifacthub.io/packages/helm/bitnami/redis

Also visit Helm documentation about chart dependencies value overrides: https://helm.sh/docs/chart_template_guide/subcharts_and_globals/#overriding-values-from-a-parent-chart

You can upgrade the helm release by executing this command:
```shell
helm upgrade fortuneCookies helm-charts/fortune-cookies/
```

Have a look to the k8s cluster with openlens or any similar tool, or with `kubectl`.

NOTE: review Helm available commands, there are very useful ones like:
```shell
helm template --help
```

## STEP 3 - Set up a cronjob that reads fortune cookies from Redis and outputs them to stdout

The cronjob has to make use of the `fortune-cookies-chef:latest` image we created during the setup and shall run every minute.

The kubernetes documentation about cronjobs may probe helpful: https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/

Can we declare multiple cronjobs just with one cronjob manifest?
Is it possible to declare a pod with a replica set with something inside writing to redis?

## STEP 4 - Set up a cronjob that queues up fortune cookies to Redis

Very similar to the previous step but with the `fortune-cookies-takeaway` image.

Are you able to show the logs of a cronjob with `kubectl` or a GUI tool.

## STEP 5 - Make an accessible endpoint that reads fortune cookies from Redis and returns them as response

Declare an ingress that exposes a 80 port outside of the cluster.
The image you should use is the `fortune-cookies-delivery` one.
You'll need to declare a pod and a service for this.

I suggest you to rely on the nginx example that was created when we created our chart.

As always, k8s documentation on ingresses is super useful: https://kubernetes.io/docs/concepts/services-networking/ingress/
