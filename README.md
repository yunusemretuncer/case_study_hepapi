# Kubernetes Case Study

This project is a simple example of how to **dockerize and deploy a Python Flask + MongoDB task manager application** using **Docker Compose, Kubernetes, Helm and has a CI/CD pipeline**.

The project is based on a cloned Python Flask + MongoDB task manager application and demonstrates three different ways to deploy the application to a Kubernetes cluster.

---

## Project Structure

The repository contains three different Kubernetes deployment approaches:

1. **Pods** – Basic Kubernetes Pods and Services
2. **Deployments** – Kubernetes Deployments and Services
3. **Helm** – Helm-based deployment using a Helm chart

---

# Running the Application with Docker Compose

First, clone the repository to your local machine.

Then, run:

```bash
docker compose up
```

This will build and start the application and MongoDB containers.

Once the containers are running, the application should be available at:

```text
http://localhost:5000
```

---

# Deploying to Kubernetes

Before deploying the application to Kubernetes, you need a local Kubernetes cluster.

You can use one of the following:

* Minikube
* Kind
* Any other local Kubernetes cluster

If you are using **Minikube with WSL**, you can find a guide for installing and configuring Minikube inside this repository.

The application can be deployed to Kubernetes in three different ways.


---

## 1. Pods Deployment

The `pods` folder contains a very basic Kubernetes configuration using:

* 2 Pods
* 2 Services

To deploy the application, run:

```bash
kubectl create -f ./pods/
```

### Accessing the Application

If Minikube is **not running inside WSL**, you can find the Minikube node IP using:

```bash
kubectl get nodes -o wide
```

Copy the Minikube node IP.

Then, check the Services:

```bash
kubectl get svc
```

Find the port exposed by the application Service.

For example:

```text
192.168.49.2:31001
```

You can then access the application from your browser using:

```text
http://192.168.49.2:31001
```

If Minikube is running **inside WSL**, you can use:

```bash
minikube service <service-name> --url
```

This command will provide a URL similar to:

```text
http://127.0.0.1:36579
```

with this URL access the application in a windows browser.

---

## 2. Deployment-Based Deployment

The `deployment` folder contains a more advanced Kubernetes configuration using:

* 2 Deployments
* 2 Services

To deploy the application, run:

```bash
kubectl create -f ./deployment/
```

Compared to the previous approach, this deployment uses Kubernetes **Deployments** instead of directly creating Pods.

Deployments provide additional features such as:

* Rolling updates
* Rollbacks
* Scaling
* Updating the application version
* Maintaining the desired number of pods(replicas)
* Automatic Pod recreation if a Pod fails

For example, you can check the status of your Deployments with:

```bash
kubectl get deployments
```

And check the running Pods with:

```bash
kubectl get pods
```

The process for accessing the application is the same as described in the previous section.

---

## 3. Helm Deployment

The `case-app` directory contains the Helm chart for deploying the application.

To deploy the application using Helm, you must have **Helm** installed on your system.

You can install the Helm chart using:

```bash
helm install <deployment-name> ./case-app
```

For example:

```bash
helm install case-app-release ./case-app
```

The `<deployment-name>` is the Helm release name.

You can use different release names to deploy multiple instances of the same Helm chart.

For example:

```bash
helm install case-app-1 ./case-app
helm install case-app-2 ./case-app
```

You can check your Helm releases with:

```bash
helm list
```

To check the Kubernetes resources created by the Helm release:

```bash
kubectl get pods
kubectl get deployments
kubectl get svc
```

To uninstall a Helm release:

```bash
helm uninstall <deployment-name>
```

For example:

```bash
helm uninstall case-app-release
```

The process for accessing the application is the same as described in the previous sections.

---

### CI/CD Pipeline

The pipeline has 2 workflows: CI and CD.

The CI workflow triggers on a push, the image gets built and tested, and then pushed into GHCR.

Before even triggering the CD, you must do some configuration: go to Settings > Actions > Runners, click New self-hosted runner, choose OS and architecture, then do the given configs. If it is a public repo, be aware of this warning given by GitHub:

> Using self-hosted runners in public repositories is not recommended. Forks of your public repository can potentially run dangerous code on your self-hosted runner by creating a pull request.

To trigger the CD, you must do it manually with workflow_dispatch: go to Actions, select the CD workflow, then click Run workflow. You must enter the desired image version to deploy and the release.name for the helm release. CD checks kubectl and helm, fetches cluster details, then proceeds to deploy it with helm.

---

# Summary

This case study demonstrates three different approaches to deploying a containerized Flask + MongoDB application to Kubernetes.

