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

## 4. Deploying the Application to AWS EKS

The application can also be deployed to Amazon EKS using `eksctl` and Helm.

The AWS deployment consists of the following components:

* Amazon ECR – stores the Docker image
* Amazon EKS – runs the Kubernetes cluster
* Amazon EBS – provides persistent storage for MongoDB
* EBS CSI Driver – allows Kubernetes to dynamically create EBS volumes
* Helm – deploys the Flask application and MongoDB

The architecture is approximately:

```text
                         AWS
                          |
                    Amazon EKS
                          |
                +---------+---------+
                |                   |
          Worker Node 1       Worker Node 2
            t3.small            t3.small
                |                   |
        +-------+------+      +-----+------+
        |              |      |            |
     Flask Pod      MongoDB   Flask Pod   System Pods
                      |
                      |
                   PVC 1Gi
                      |
                   GP3 EBS
```

### Prerequisites

Before creating the EKS cluster, install/configure:

* AWS CLI
* kubectl
* eksctl
* Helm
* AWS credentials

Check the installations:

```bash
aws --version
kubectl version --client
eksctl version
helm version
```

Configure AWS credentials:

```bash
aws configure
```

Verify that AWS CLI can access the account:

```bash
aws sts get-caller-identity
```

### 4.1 Push the Docker Image to Amazon ECR

Before deploying the application to EKS, the Docker image must be pushed to Amazon Elastic Container Registry (ECR).

First, create an ECR repository:

```bash
aws ecr create-repository \
  --repository-name flask-task-manager \
  --region eu-central-1
```

Authenticate Docker with ECR:

```bash
aws ecr get-login-password \
  --region eu-central-1 | \
  docker login \
  --username AWS \
  --password-stdin \
  <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com
```

Build the application image:

```bash
docker build -t flask-task-manager .
```

Tag the image for ECR:

```bash
docker tag flask-task-manager:latest \
  <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/flask-task-manager:latest
```

Push the image to ECR:

```bash
docker push \
  <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/flask-task-manager:latest
```

You can verify that the image was uploaded successfully:

```bash
aws ecr describe-images \
  --repository-name flask-task-manager \
  --region eu-central-1
```

The resulting image URI is:

```text
<AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/flask-task-manager:latest
```

This image URI is then used in the Helm `values.yaml` file:

```yaml
app:
  image: <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/flask-task-manager:latest
```

Replace `<AWS_ACCOUNT_ID>` with your AWS account ID.

### 4.2 Create the EKS Cluster

The EKS cluster configuration is located in:

```text
eks-cluster.yaml
```

Example:

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: flask-cluster
  region: eu-central-1
  version: "1.34"

managedNodeGroups:
  - name: app-nodes
    instanceType: t3.small
    desiredCapacity: 2
    minSize: 1
    maxSize: 2
```

Create the cluster:

```bash
eksctl create cluster -f eks-cluster.yaml
```

This creates:

```text
EKS Cluster
    |
    +-- flask-cluster
          |
          +-- Managed Node Group
                |
                +-- app-nodes
                      |
                      +-- t3.small
                      +-- t3.small
```

The desiredCapacity is the initial number of nodes.

```text
desiredCapacity: 2
```

means that two worker nodes should initially be created.

The autoscaling limits are:

```text
minSize: 1
maxSize: 2
```

Therefore, the node group can contain between 1 and 2 nodes.

Check the cluster:

```bash
eksctl get cluster --region eu-central-1
```

Check the node group:

```bash
eksctl get nodegroup \
  --cluster flask-cluster \
  --region eu-central-1
```

Check Kubernetes nodes:

```bash
kubectl get nodes
```

Expected result:

```text
NAME                                             STATUS   ROLES
ip-xxx.eu-central-1.compute.internal            Ready    <none>
ip-xxx.eu-central-1.compute.internal            Ready    <none>
```

#### Why Two Nodes Are Useful

Initially, a single t3.small node was insufficient for the complete workload.

The node had limited resources and was already running several EKS system components:

* aws-node
* coredns
* kube-proxy
* metrics-server
* eks-pod-identity-agent

When the application attempted to run:

* Flask
* MongoDB

the scheduler could report:

```text
Too many pods
```

Adding a second node provides additional pod capacity.

It also allows system pods such as CoreDNS and Metrics Server to move between nodes during node maintenance/draining.

#### Scaling the Node Group

The node group configuration is:

```text
desiredCapacity: 2
minSize: 1
maxSize: 2
```

This allows up to two worker nodes.

The node group can also be scaled with eksctl.

For example:

```bash
eksctl scale nodegroup \
  --cluster flask-cluster \
  --region eu-central-1 \
  --name app-nodes \
  --nodes 2
```

The maxSize must be at least as large as the requested desired capacity.

For example:

```text
maxSize: 1
```

cannot be scaled to:

```text
desired = 2
```

Therefore the cluster configuration should allow:

```text
minSize: 1
desiredCapacity: 2
maxSize: 2
```

### 4.3 Configure the EBS CSI Driver

EKS provides several Kubernetes add-ons.

Check them with:

```bash
eksctl get addon \
  --cluster flask-cluster \
  --region eu-central-1
```

For persistent storage, the most important component is the:

```text
aws-ebs-csi-driver
```

The EBS CSI Driver allows Kubernetes to dynamically create Amazon EBS volumes for PersistentVolumeClaims.

#### Install the EBS CSI Driver

Create the EBS CSI Driver:

```bash
eksctl create addon \
  --name aws-ebs-csi-driver \
  --cluster flask-cluster \
  --region eu-central-1
```

The EBS CSI Driver is responsible for connecting Kubernetes persistent storage with Amazon EBS.

The architecture becomes:

```text
MongoDB
   |
   v
PersistentVolumeClaim
   |
   v
EBS CSI Driver
   |
   v
Amazon EBS GP3 Volume
```

#### EKS Pod Identity

The EBS CSI Driver needs AWS IAM permissions to create and manage EBS volumes.

For this cluster, EKS Pod Identity is used.

Install the Pod Identity Agent:

```bash
eksctl create addon \
  --cluster flask-cluster \
  --name eks-pod-identity-agent
```

Verify:

```bash
eksctl get addon \
  --cluster flask-cluster \
  --region eu-central-1
```

The result should contain:

```text
eks-pod-identity-agent    ACTIVE
```

#### IAM Role for the EBS CSI Driver

An IAM role is created for the EBS CSI Driver.

Example role:

```text
AmazonEKS_EBS_CSI_DriverRole
```

Get the role ARN:

```bash
ROLE_ARN=$(aws iam get-role \
  --role-name AmazonEKS_EBS_CSI_DriverRole \
  --query 'Role.Arn' \
  --output text)
```

Check it:

```bash
echo "$ROLE_ARN"
```

Create the Pod Identity Association:

```bash
eksctl create podidentityassociation \
  --cluster flask-cluster \
  --region eu-central-1 \
  --namespace kube-system \
  --service-account-name ebs-csi-controller-sa \
  --role-arn "$ROLE_ARN"
```

This connects:

```text
Kubernetes ServiceAccount
        |
        v
ebs-csi-controller-sa
        |
        v
EKS Pod Identity
        |
        v
IAM Role
        |
        v
Amazon EBS permissions
```

Check the EBS CSI pods:

```bash
kubectl get pods -n kube-system | grep ebs
```

They should eventually show:

```text
ebs-csi-controller-xxxxx   6/6   Running
ebs-csi-controller-xxxxx   6/6   Running
ebs-csi-node-xxxxx         3/3   Running
```

### 4.4 Configure the GP3 StorageClass

The EKS-specific Kubernetes configuration is located in:

```text
k8s/
```

The StorageClass is:

```text
k8s/storageclass.yaml
```

Configuration:

```yaml
apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:
  name: gp3

provisioner: ebs.csi.aws.com

parameters:
  type: gp3
  fsType: ext4

volumeBindingMode: WaitForFirstConsumer

allowVolumeExpansion: true

reclaimPolicy: Delete
```

Apply it:

```bash
kubectl apply -f k8s/storageclass.yaml
```

Check it:

```bash
kubectl get storageclass
```

Expected:

```text
NAME   PROVISIONER       RECLAIMPOLICY   VOLUMEBINDINGMODE
gp3    ebs.csi.aws.com   Delete          WaitForFirstConsumer
```

#### Understanding the StorageClass

**provisioner**

```yaml
provisioner: ebs.csi.aws.com
```

This tells Kubernetes to use the AWS EBS CSI Driver.

**type**

```yaml
type: gp3
```

The underlying AWS EBS volume will be a GP3 volume.

GP3 is a general-purpose SSD storage type suitable for applications such as MongoDB.

**fsType**

```yaml
fsType: ext4
```

The filesystem used by the mounted volume is ext4.

**volumeBindingMode**

```yaml
volumeBindingMode: WaitForFirstConsumer
```

This is especially important in EKS.

The volume is not immediately created when the PVC is created.

Instead, Kubernetes waits until the pod using the PVC is scheduled.

This allows Kubernetes/AWS to select an appropriate Availability Zone for the EBS volume.

For example:

```text
MongoDB Pod
    |
    v
Node in eu-central-1a
    |
    v
EBS Volume
    |
    v
eu-central-1a
```

This avoids creating an EBS volume in an Availability Zone where the pod cannot use it.

**allowVolumeExpansion**

```yaml
allowVolumeExpansion: true
```

This allows the PVC to be expanded later.

For example, a:

```text
1Gi
```

volume could later be increased to:

```text
5Gi
```

without recreating the application storage.

**reclaimPolicy**

```yaml
reclaimPolicy: Delete
```

When the PVC is deleted, the dynamically created PV/EBS volume can also be deleted.

This is convenient for a case study/test environment.

For production databases, a different lifecycle strategy may be preferred to prevent accidental data loss.

### 4.5 Deploy the Helm Chart to EKS

The Helm chart is located in:

```text
eks/
```

Its structure is:

```text
eks/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── api-deployment.yaml
    ├── api-service.yaml
    ├── db-statefulset.yaml
    ├── db-service.yaml
    └── db-secret.yaml
```

The important difference from the earlier Kubernetes deployment is that MongoDB is deployed as a:

```text
StatefulSet
```

rather than a simple Deployment.

This is appropriate for a stateful database because StatefulSets provide stable pod identity and work naturally with persistent storage.

#### MongoDB StatefulSet

The MongoDB configuration is located at:

```text
eks/templates/db-statefulset.yaml
```

The important section is:

```yaml
volumeClaimTemplates:
  - metadata:
      name: mongo-data

    spec:
      accessModes:
        - ReadWriteOnce

      storageClassName: gp3

      resources:
        requests:
          storage: 1Gi
```

This tells Kubernetes:

Create a 1Gi persistent volume for the MongoDB pod using the gp3 StorageClass.

The relationship is:

```text
StatefulSet
    |
    +-- volumeClaimTemplates
            |
            v
          PVC
            |
            v
          PV
            |
            v
        AWS EBS GP3
```

When the StatefulSet creates:

```text
flask-app-db-0
```

Kubernetes creates a PVC similar to:

```text
mongo-data-flask-app-db-0
```

Check it:

```bash
kubectl get pvc
```

Example:

```text
NAME                         STATUS   VOLUME
mongo-data-flask-app-db-0    Bound    pvc-xxxx
```

Then:

```bash
kubectl get pv
```

will show the dynamically created PersistentVolume.

#### MongoDB Service

The MongoDB service is:

```text
flask-app-db
```

It is a headless service:

```yaml
clusterIP: None
```

This allows the StatefulSet to have stable network identity.

The application connects to MongoDB using:

```text
mongodb://root:example@flask-app-db:27017/
```

The Kubernetes DNS system resolves:

```text
flask-app-db
```

to the MongoDB service.

#### Kubernetes Secret

MongoDB credentials are stored in:

```text
eks/templates/db-secret.yaml
```

The Secret contains:

* username
* password
* uri

The MongoDB StatefulSet reads the username/password from the Secret.

The Flask application reads the MongoDB URI from the same Secret.

This avoids hardcoding the MongoDB connection string directly into the Deployment.

Check the Secret:

```bash
kubectl get secret flask-app-db-secret
```

To inspect the URI:

```bash
kubectl get secret flask-app-db-secret \
  -o jsonpath='{.data.uri}' | base64 -d

echo
```

#### Install the Helm Chart on EKS

Once the EKS cluster, EBS CSI Driver and StorageClass are ready:

```bash
helm install flask-app ./eks
```

Check the release:

```bash
helm list
```

Check the pods:

```bash
kubectl get pods
```

Expected:

```text
flask-app-app-xxxxx     1/1     Running
flask-app-app-xxxxx     1/1     Running
flask-app-db-0          1/1     Running
```

Check the PVC:

```bash
kubectl get pvc
```

Expected:

```text
mongo-data-flask-app-db-0   Bound   pvc-xxxxx   1Gi   RWO   gp3
```

### 4.6 Verify the Deployment

A useful verification sequence is:

```bash
kubectl get nodes
kubectl get pods
kubectl get svc
kubectl get pvc
kubectl get pv
kubectl get storageclass
eksctl get addon \
  --cluster flask-cluster \
  --region eu-central-1
```

Everything should be healthy before considering the deployment complete.

### 4.7 Access the Application

The Flask application uses a Kubernetes:

```text
LoadBalancer
```

service.

Check it:

```bash
kubectl get svc
```

Example:

```text
NAME             TYPE           CLUSTER-IP      EXTERNAL-IP
flask-app-app    LoadBalancer   10.100.x.x      xxxxx.elb.amazonaws.com
flask-app-db     ClusterIP      None            <none>
```

AWS automatically provisions an AWS load balancer for the application service.

The architecture is:

```text
Internet
   |
   v
AWS Load Balancer
   |
   v
flask-app-app Service
   |
   +------------+
   |            |
   v            v
Flask Pod    Flask Pod
                |
                v
          flask-app-db
                |
                v
            MongoDB
                |
                v
            EBS GP3
```

Get the LoadBalancer address:

```bash
kubectl get svc flask-app-app
```

Then open the EXTERNAL-IP hostname in a browser.

### 4.8 Delete the EKS Resources

When the case study is finished, remove the Helm deployment first:

```bash
helm uninstall flask-app
```

Verify:

```bash
kubectl get pods
kubectl get pvc
```

Because the StorageClass uses:

```yaml
reclaimPolicy: Delete
```

the dynamically provisioned EBS volume associated with the PVC can be deleted when the PVC is removed.

Then delete the StorageClass:

```bash
kubectl delete -f k8s/storageclass.yaml
```

Finally, delete the EKS cluster:

```bash
eksctl delete cluster \
  -f eks-cluster.yaml
```

or:

```bash
eksctl delete cluster \
  --name flask-cluster \
  --region eu-central-1
```

Verify that the cluster has been removed:

```bash
eksctl get cluster --region eu-central-1
```

### Configuration Files Reference

The `k8s` directory contains AWS-specific Kubernetes resources:

```text
k8s/
└── storageclass.yaml
```

**k8s/storageclass.yaml** defines how Kubernetes should dynamically provision persistent storage in AWS. This file does not create an EBS volume immediately — it defines a storage template. The actual volume is created when the MongoDB StatefulSet creates a PVC:

```text
db-statefulset.yaml
        |
        v
volumeClaimTemplates
        |
        v
PersistentVolumeClaim
        |
        v
StorageClass: gp3
        |
        v
EBS CSI Driver
        |
        v
Amazon EBS GP3
```

The EKS-specific files and their responsibilities are:

| File | Responsibility |
|---|---|
| `eks-cluster.yaml` | Creates/configures the AWS EKS cluster and worker nodes |
| `k8s/storageclass.yaml` | Defines AWS EBS GP3 persistent storage |
| `eks/Chart.yaml` | Defines the Helm chart |
| `eks/values.yaml` | Contains configurable application/database values, including the ECR image URI |
| `eks/templates/api-deployment.yaml` | Deploys Flask application |
| `eks/templates/api-service.yaml` | Exposes Flask application |
| `eks/templates/db-statefulset.yaml` | Deploys MongoDB with persistent storage |
| `eks/templates/db-service.yaml` | Provides internal MongoDB DNS/networking |
| `eks/templates/db-secret.yaml` | Stores MongoDB credentials and URI |

### Deployment Flow Overview

The complete process can be summarized as:

```text
1. Configure AWS CLI
        |
        v
2. Push Docker Image to Amazon ECR
        |
        v
3. Create EKS Cluster
        |
        v
4. Create Managed Node Group
        |
        v
5. Install EBS CSI Driver
        |
        v
6. Install EKS Pod Identity Agent
        |
        v
7. Configure IAM Role
        |
        v
8. Create Pod Identity Association
        |
        v
9. Create GP3 StorageClass
        |
        v
10. Install Helm Chart (using the ECR image)
        |
        +----------------------+
        |                      |
        v                      v
    Flask                  MongoDB
        |                      |
        |                      v
        |                     PVC
        |                      |
        |                      v
        |                  EBS CSI Driver
        |                      |
        |                  EBS GP3
        |
        v
LoadBalancer Service
        |
        v
AWS Load Balancer
        |
        v
      User
```

### Local Kubernetes vs AWS EKS

The project now demonstrates two different environments.

**Local Kubernetes**

```text
Docker Compose
      |
      v
Minikube / Kind
      |
      v
Pods / Deployments / Helm
```

**AWS**

```text
AWS
 |
 +-- ECR
 |
 +-- EKS
      |
      +-- Managed Node Group
      |
      +-- EBS CSI Driver
      |
      +-- EKS Pod Identity
      |
      +-- GP3 EBS
      |
      +-- Helm
      |
      +-- Flask
      |
      +-- MongoDB
```

This makes the case study more complete because it demonstrates the progression from containerization → basic Kubernetes → Deployments → Helm → container registry → managed Kubernetes on AWS → persistent cloud storage.

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