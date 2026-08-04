# Running a Local Kubernetes Cluster on WSL with Docker Desktop

For this project, I used **Minikube** running inside **WSL2 (Ubuntu)** because I already use Docker Desktop with WSL2 integration. After researching where to run on windows or wsl my conclusion was wsl.


## 1. Enable Kubernetes in Docker Desktop

Open Docker Desktop and navigate to:

```
Settings → Kubernetes → Enable Kubernetes
```

Wait until Kubernetes has finished starting before continuing.

## 2. Install Minikube

Follow the official installation guide:

https://minikube.sigs.k8s.io/docs/start/

For me it was **Linux x86-64** inside WSL to learn yours , run:

```bash
uname -m
```

now for **Linux x86-64**, run:

```bash
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64

sudo install minikube-linux-amd64 /usr/local/bin/minikube

rm minikube-linux-amd64
```

Start the local Kubernetes cluster:

```bash
minikube start
```

If the command completes successfully, your local Kubernetes cluster is ready.


Check the cluster status:

```bash
minikube status
```


Expected output:

```text
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```
