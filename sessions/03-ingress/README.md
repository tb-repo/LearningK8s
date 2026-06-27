# Session 03: Ingress With Multiple Microservices

This session refactors the app deployment shape from one Flask service into separate microservices behind one Ingress.

It reuses the PostgreSQL StatefulSet pattern from Session 02. The new idea in this session is external HTTP routing to multiple internal Services.

App images:

```text
prashantdey/appk8stutorial:user-svc-2.0
prashantdey/appk8stutorial:app-svc-2.0
prashantdey/appk8stutorial:frontend-svc-2.0
```

Each microservice has its own folder and Dockerfile under `../../app/`:

- `frontend/frontend.py`: browser UI on port `5000`.
- `user-service/user_service.py`: user API on port `5001`.
- `app-service/app_service.py`: message/application API on port `5002`.

Build the images from the `app` folder:

```bash
docker build -t prashantdey/appk8stutorial:user-svc-2.0 ./user-service
docker build -t prashantdey/appk8stutorial:app-svc-2.0 ./app-service
docker build -t prashantdey/appk8stutorial:frontend-svc-2.0 ./frontend
```

Push those tags before deploying to EKS:

```bash
docker push prashantdey/appk8stutorial:user-svc-2.0
docker push prashantdey/appk8stutorial:app-svc-2.0
docker push prashantdey/appk8stutorial:frontend-svc-2.0
```

The Ingress gives one external address, such as the AWS load balancer DNS name, and routes paths to different internal Services:

```text
http://xyz.com/          -> frontend
http://xyz.com/api/users -> user-service
http://xyz.com/api/apps  -> app-service
```

Here `xyz.com` means the Ingress load balancer address. It can be the AWS ALB DNS name directly, or a custom DNS name that points to it.

## EKS Requirement

For this session on EKS, install the AWS Load Balancer Controller before applying the Ingress manifest.

Check whether an IngressClass exists:

```bash
kubectl get ingressclass
```

This lesson uses:

```text
ingressClassName: alb
```

## To create an Application Load Balancer as it if it is not created yet:

```bash
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json" -OutFile "iam_policy.json"
```

## Create the AWS IAM Policy

```bash
aws iam create-policy --policy-name TBAWSLoadBalancerControllerIAMPolicy --policy-document file://iam_policy.json
```
## Get the ARN of the policy:

Eg:
"Arn": "arn:aws:iam::386346184566:policy/TBAWSLoadBalancerControllerIAMPolicy"

## 2. Create an IAM Role and Service Account using eksctlThis links a Kubernetes service account to the AWS IAM policy:

a. Activate the OIDC Provider

Execute the exact:
```bash
eksctl utils associate-iam-oidc-provider --region=ap-south-1 --cluster=tb-k8s-cluster-1 --approve
```
b. Create IAM Service Account:

```bash
eksctl create iamserviceaccount `
  --cluster=tb-k8s-cluster-1 `
  --namespace=kube-system `
  --name=aws-load-balancer-controller `
  --role-name TBAmazonEKSLoadBalancerControllerRole `
  --attach-policy-arn=arn:aws:iam::376432388605:policy/TBAWSLoadBalancerControllerIAMPolicy `
  --approve
  ```

## Install via Helm

Add the repository and install the controller inside the kube-system namespace:

# Add EKS charts

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update eks
```
## Install the controller (the chart automatically deploys the alb IngressClass)

```bash
helm install aws-load-balancer-controller eks/aws-load-balancer-controller `
  -n kube-system `
  --set clusterName=tb-k8s-cluster-1 `
  --set serviceAccount.create=false `
  --set serviceAccount.name=aws-load-balancer-controller
```
Check whether an IngressClass exists now:

```bash
kubectl get ingressclass
```
## Sub-Session Order

Follow the sub-sessions in this order:

1. `subsessions/01-shared-config`: create Namespace, ConfigMap, and Secret.

Before moving to point 5 create the required role for the EKS to use EBS:

```bash
eksctl utils associate-iam-oidc-provider --region=ap-south-1 --cluster=tb-k8s-cluster-1 --approve
```

```bash
eksctl create iamserviceaccount `
  --name ebs-csi-controller-sa `
  --namespace kube-system `
  --cluster=tb-k8s-cluster-1 `
  --region=ap-south-1 `
  --attach-policy-arn=arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy `
  --approve `
  --role-only `
  --role-name TB_EKS_EBS_CSI_DriverRole
  ```

Install or Update the AWS EBS Add-ons

```bash
eksctl create addon --cluster=tb-k8s-cluster-1 --region=ap-south-1 --name=eks-pod-identity-agent
```

```bash
aws iam update-assume-role-policy --role-name TB_EKS_EBS_CSI_DriverRole --policy-document file://iam_trust_policy.json
```

```bash
eksctl create podidentityassociation `
  --cluster=tb-k8s-cluster-1 `
  --region=ap-south-1 `
  --namespace=kube-system `
  --service-account-name=ebs-csi-controller-sa `
  --role-arn=arn:aws:iam::376432388605:role/TB_EKS_EBS_CSI_DriverRole
```
```bash
eksctl create addon `
  --name aws-ebs-csi-driver `
  --cluster=tb-k8s-cluster-1 `
  --region=ap-south-1 `
  --force
```

Wait for the add-on to get successfully created.

```bash
kubectl get pods -n kube-system
```
Check whether ebs-csi is getting listed and running successfully.

Verify the EBS Controller Pods:

```bash
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-ebs-csi-driver
```

2. `subsessions/02-storageclass`: create the EKS gp3 StorageClass.
3. `subsessions/03-postgres-statefulset`: run PostgreSQL as a StatefulSet.
4. `subsessions/04-api-microservices`: deploy `user-service` and `app-service` as internal Services on different ports.
5. `subsessions/05-frontend`: deploy the frontend as an internal Service.
6. `subsessions/06-ingress`: expose all three Services through one Ingress.

## Target Shape By The End

```text
Browser
  -> Ingress /           -> frontend Service    -> frontend Deployment    -> port 5000
  -> Ingress /api/users  -> user-service        -> user-service Deployment -> port 5001
  -> Ingress /api/apps   -> app-service         -> app-service Deployment  -> port 5002

frontend
  -> user-service:5001
  -> app-service:5002

user-service and app-service
  -> PostgreSQL Service
    -> PostgreSQL StatefulSet
      -> PVC from volumeClaimTemplates
```

## Full Apply Order

From `sessions/03-ingress`:

```bash
kubectl apply -f subsessions/01-shared-config/
kubectl apply -f subsessions/02-storageclass/
kubectl apply -f subsessions/03-postgres-statefulset/
kubectl apply -f subsessions/04-api-microservices/
kubectl apply -f subsessions/05-frontend/
kubectl apply -f subsessions/06-ingress/
```

## Get The Load Balancer Address

```bash
kubectl get ingress -n tb-app-ingress
kubectl get pods -n tb-app-ingress
```

Wait until the `ADDRESS` column is populated. Then test:

```bash
export APP_DNS=<ingress-address>

curl http://$APP_DNS/api/users
curl http://$APP_DNS/api/users/stats
curl http://$APP_DNS/api/apps
curl http://$APP_DNS/api/apps/messages
curl http://$APP_DNS/api/apps/stats
```

Open the frontend:

```text
http://<ingress-address>
```

## Cleanup

From `sessions/03-ingress`:

```bash
kubectl delete -f subsessions/06-ingress/ --ignore-not-found
kubectl delete -f subsessions/05-frontend/ --ignore-not-found
kubectl delete -f subsessions/04-api-microservices/ --ignore-not-found
kubectl delete -f subsessions/03-postgres-statefulset/ --ignore-not-found
kubectl delete pvc -n app-ingress -l app=postgres,session=ingress --ignore-not-found
kubectl delete -f subsessions/02-storageclass/ --ignore-not-found
kubectl delete -f subsessions/01-shared-config/ --ignore-not-found
```

## Review Questions

1. Why do the frontend and API Services remain `ClusterIP`?
2. What does the Ingress controller create in AWS?
3. Why is `/api/users` routed to a different Service from `/api/apps`?
4. Why does the frontend call APIs by Kubernetes Service DNS inside the cluster?
5. How would a custom domain point to the Ingress load balancer?

## Review Answers

1. They are internal backends; Ingress exposes external access and routes to ClusterIP Services.
2. An external Load Balancer (ELB/NLB) and related cloud resources (target groups, security groups).
3. Ingress path rules map different URL paths to different backend Services.
4. Service DNS provides stable, internal service discovery without external routing.
5. Point the custom domain's DNS (A/CNAME) to the load balancer's DNS name or IP.
