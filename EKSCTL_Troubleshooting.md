# EKSCTL Troubleshooting Playbook

This document helps troubleshoot EKS clusters created and managed with `eksctl`.
It is designed to be a companion to the Kubectl troubleshooting flow, focusing on EKS cluster creation,
nodegroup management, AWS IAM, kubeconfig access, and common AWS/EKS issues.

---

## Phase 1: Preflight checks

Before running `eksctl`, confirm your AWS credentials and CLI environment are correct.

### 1. Verify AWS credentials and region

```bash
aws sts get-caller-identity
aws configure list
aws configure get region
```

### 2. Confirm `eksctl` and `kubectl` versions

```bash
eksctl version
kubectl version --client
```

Ensure `eksctl` supports the target EKS version and your AWS CLI is configured for the same region.

---

## Phase 2: Cluster creation issues

### 1. Create cluster command structure

```bash
eksctl create cluster \
  --name tb-k8s-cluster-1 \
  --region ap-south-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 3
```

### 2. Common failures

- `AccessDenied` or IAM errors: the IAM identity does not have permissions to create VPCs, EC2 instances, IAM roles, or CloudFormation stacks.
- `Timeout` during creation: AWS resource provisioning is slow or quota limits are reached.
- `VPC` or subnet issues: if you provide a custom VPC, ensure subnets are private/public correctly configured.

### 3. Troubleshoot failed cluster creation

```bash
eksctl utils describe-stacks --cluster tb-k8s-cluster-1 --region ap-south-1
```

Then inspect the failed CloudFormation stack in the AWS Console or `aws cloudformation describe-stack-events`.

---

## Phase 3: Nodegroup and scaling issues

### 1. Check nodegroup status

```bash
eksctl get nodegroup --cluster tb-k8s-cluster-1 --region ap-south-1
```

### 2. Describe the nodegroup for details

```bash
eksctl describe nodegroup --cluster tb-k8s-cluster-1 --region ap-south-1 --name standard-workers
```

### 3. Common nodegroup problems

- `Scaling issue`: nodegroup cannot add nodes because AWS quotas, EC2 limits, or insufficient IP addresses on the instance type.
- `Node not Ready`: instance launched but cluster bootstrapping failed or kubelet cannot register to the EKS control plane.
- `Not enough pods`: ENI/IP limit reached for the instance type.

### 4. Verify EC2 and VPC limits

```bash
aws ec2 describe-account-attributes --attribute-names max-instances
aws ec2 describe-vpc-attribute --vpc-id <vpc-id> --attribute enableDnsSupport
```

---

## Phase 4: Kubeconfig and cluster access

### 1. Generate kubeconfig for the cluster

```bash
aws eks --region ap-south-1 update-kubeconfig --name tb-k8s-cluster-1
```

### 2. Verify cluster access

```bash
kubectl get nodes
kubectl get pods --all-namespaces
```

### 3. Common access problems

- `Unable to connect to the server`: kubeconfig points to the wrong cluster or EKS cluster endpoint is not available.
- `Forbidden`: AWS IAM user/role lacks permission to call EKS or STS.
- `NoSuchKey`/credential errors: wrong AWS profile or expired session token.

---

## Phase 5: Addon and IAM troubleshooting

### 1. EKS IAM OIDC provider

Confirm the cluster has an OIDC provider associated:

```bash
eksctl utils associate-iam-oidc-provider --cluster tb-k8s-cluster-1 --region ap-south-1 --approve
```

If the provider already exists, `eksctl` will report it.

### 2. Create IRSA service accounts

```bash
eksctl create iamserviceaccount \
  --cluster tb-k8s-cluster-1 \
  --namespace kube-system \
  --name cluster-autoscaler \
  --attach-policy-arn arn:aws:iam::975050024946:policy/AmazonEKSClusterAutoscalerPolicy \
  --override-existing-serviceaccounts \
  --approve \
  --region ap-south-1
```

### 3. Addon installation and status

Install the EBS CSI driver:

```bash
eksctl create addon --name aws-ebs-csi-driver --cluster tb-k8s-cluster-1 --region ap-south-1
```

### 4. Common addon failures

- Permission denied when creating IAM roles or policies.
- Addon install hangs because the cluster is not yet healthy.
- CSI driver pods `CrashLoopBackOff`: missing IAM permissions or incorrect service account setup.

### 5. Verify service account permissions

```bash
aws eks describe-nodegroup --cluster-name tb-k8s-cluster-1 --nodegroup-name standard-workers --region ap-south-1 --query "nodegroup.nodeRole" --output text
aws iam attach-role-policy --role-name <NodeInstanceRoleName> --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
```

---

## Phase 6: Cluster deletion / cleanup

### 1. Delete cluster safely

```bash
eksctl delete cluster --name tb-k8s-cluster-1 --region ap-south-1
```

### 2. If deletion fails

- Check for stuck CloudFormation stacks in the AWS Console.
- Remove dependent resources that are not managed by `eksctl` (for example, custom VPC endpoints or manually created load balancers).

---

## Quick EKSCTL troubleshooting checklist

1. Confirm AWS CLI and `eksctl` are using the same region and credentials.
2. Validate cluster creation permissions and CloudFormation stack status.
3. Check nodegroup health and AWS quotas for instances and ENI limits.
4. Refresh kubeconfig and verify `kubectl` can reach the cluster.
5. Confirm OIDC and IRSA setup before deploying addons.
6. Inspect CloudWatch logs or pod logs for addon and bootstrap failures.

---

## When to add more detail to the Kubectl playbook

The existing Kubectl troubleshooting file is strong for general Kubernetes application issues.
Add more detail only if you want:

- EKS-specific networking issues (ALB, NLB, security groups)
- AWS Load Balancer Controller diagnosis
- Cluster autoscaler / node scaling error messages
- Fargate profile validation and pod placement

A separate `EKSCTL_Troubleshooting.md` is the right place for AWS/EKS cluster lifecycle issues.
