# Pipelines with Spark

## Setup

### Install kind

#### MacOS
```shell
brew install kind
```

#### Linux
```shell
# For AMD64 / x86_64
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-amd64
# For ARM64
[ $(uname -m) = aarch64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-arm64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### Install kubectl

#### MacOS
```shell
brew install kubernetes-cli
```

#### Linux
```shell
# We assume you have curl installed
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### Setup Kubernetes

Create Docker registry and Kubernetes cluster
```shell
./kubernetes/kind-with-registry.sh
```

Create and configure Kubernetes service account for Spark
```shell
kubectl create serviceaccount spark
kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default
```

### Setup Python Environment
```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install build
```

### Build Spark Image with Python 3.12
Why? Because I am angry that the official Spark image is using Python 3.8.10. **That was three years ago.**

```shell
docker build -t localhost:5001/spark:python3.12 -f Dockerfile-spark .
docker push localhost:5001/spark:python3.12
```

### Get the Data
On Kaggle, download the [India Higher Education Analytics dataset](https://www.kaggle.com/datasets/rajanand/aishe) and unpack
it to a folder `data` within this project directory.

## Run
Note that the code as-is will likely hit an OutOfMemory (OOM) error.

```shell
docker build -t localhost:5001/pipelines-with-spark:latest .
docker push localhost:5001/pipelines-with-spark:latest
spark-submit \
  --master "k8s://$(kubectl config view --minify --output jsonpath='{.clusters[*].cluster.server}')" \
  --deploy-mode cluster \
  --name pipelines-with-spark \
  --conf spark.kubernetes.namespace=default \
  --conf spark.kubernetes.container.image=localhost:5001/pipelines-with-spark:latest \
  --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
  local:///opt/spark/work-dir/main.py
```

## Cleanup

### Delete Kubernetes Cluster
```shell
kind delete cluster
docker stop kind-registry && docker rm kind-registry
```
