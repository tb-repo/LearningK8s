eksctl create cluster --name tb-k8s-cluster-1 --region ap-south-1 --nodegroup-name standard-workers --node-type t3.small --nodes 2 --nodes-min 2 --nodes-max 3 --version 1.36 

eksctl create cluster --name my-fargate-cluster --region us-east-1 --fargate


# EKS Deployment

Create Cluster:
```bash
eksctl create cluster --name tb-k8s-cluster-1 --region ap-south-1 --nodegroup-name standard-workers --node-type t3.medium --nodes 2 --nodes-min 2 --nodes-max 3
```

Configuring the kubectl with eks cluster:
```bash
aws eks --region ap-south-1 update-kubeconfig --name tb-k8s-cluster-1
```

Apply the k8s files:
```bash
kubectl apply -f Deployment.yaml
```

To Monitor:
```bash
kubectl get services --watch
```

Delete EKS Cluster:
```bash
eksctl delete cluster --name tb-k8s-cluster-1 --region ap-south-1
```

Find all contexts (Cluster):
```bash
kubectl config get-contexts
```

Switching to the cluster:
```bash
kubectl config use-context docker-desktop
```

Add autoscaler:


```bash
aws eks describe-nodegroup --cluster-name sample-cluster-2 --nodegroup-name standard-workers --region ap-south-1 --query "nodegroup.resources.autoScalingGroups[0].name" --output text

aws autoscaling create-or-update-tags --region ap-south-1  --tags Key=k8s.io/cluster-autoscaler/enabled,Value=true,ResourceId=eks-standard-workers-f2ce10d0-68c7-ba39-86a7-ae61262160a3,ResourceType=auto-scaling-group,PropagateAtLaunch=true Key=k8s.io/cluster-autoscaler/sample-cluster-2,Value=owned,ResourceId=eks-standard-workers-f2ce10d0-68c7-ba39-86a7-ae61262160a3,ResourceType=auto-scaling-group,PropagateAtLaunch=true

aws autoscaling describe-tags --region ap-south-1 --filters "Name=auto-scaling-group,Values=eks-standard-workers-f2ce10d0-68c7-ba39-86a7-ae61262160a3"
```

Adding the oidc:

```bash
eksctl utils associate-iam-oidc-provider --cluster sample-cluster-2 --region ap-south-1 --approve
aws iam create-policy --policy-name AmazonEKSClusterAutoscalerPolicy --policy-document file://cluster-autoscaler-policy.json
```

create irsa account
```bash
eksctl create iamserviceaccount --cluster sample-cluster-2 --namespace kube-system --name cluster-autoscaler --attach-policy-arn arn:aws:iam::975050024946:policy/AmazonEKSClusterAutoscalerPolicy  --override-existing-serviceaccounts --approve --region ap-south-1
```

install cluster via helm

```bash

helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm repo update

helm upgrade --install cluster-autoscaler autoscaler/cluster-autoscaler --namespace kube-system --set autoDiscovery.clusterName=sample-cluster-2 --set awsRegion=ap-south-1 --set rbac.serviceAccount.create=false --set rbac.serviceAccount.name=cluster-autoscaler --set extraArgs.balance-similar-node-groups=true --set extraArgs.skip-nodes-with-system-pods=false --set extraArgs.skip-nodes-with-local-storage=false
```

verify if it is running:
```bash
kubectl -n kube-system get pods | findstr autoscaler
kubectl -n kube-system logs -l "app.kubernetes.io/name=aws-cluster-autoscaler,app.kubernetes.io/instance=cluster-autoscaler" --tail=200 -f
```

install ebs-csi addon driver:

```bash
eksctl create addon --name aws-ebs-csi-driver --cluster sample-cluster-2 --region ap-south-1
```

```bash
aws eks describe-nodegroup --cluster-name sample-cluster-2 --nodegroup-name standard-workers --region ap-south-1 --query "nodegroup.nodeRole" --output text
aws iam attach-role-policy --role-name eksctl-sample-cluster-2-nodegroup--NodeInstanceRole-LyzMqAogveTM --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
```