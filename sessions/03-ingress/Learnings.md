# Learnings

## Core Architecture & Ingress

### Kubernetes Service vs Ingress
- `Service(type: LoadBalancer)` creates a Layer 4 load balancer.
- It forwards traffic at the network layer without inspecting HTTP routes.
- `Ingress` provides Layer 7 routing, allowing one external load balancer to serve multiple applications.
- Ingress can route based on hostnames and URL paths.

### AWS Load Balancer Controller
- Required to use AWS Application Load Balancers (ALB) with EKS.
- Uses annotations such as `alb.ingress.kubernetes.io/scheme: internet-facing`.
- When `target-type: ip` is set, ALB routes traffic directly to Pod IPs.

## Persistent Storage (EBS CSI Driver)

### Driver Purpose
- The Amazon EBS CSI driver manages the lifecycle of AWS EBS volumes.
- It enables dynamic provisioning, resizing, and snapshotting through Kubernetes APIs.

### Installation
- In modern EKS versions (1.23+), the EBS CSI driver is available as a managed add-on.
- It can be installed via AWS Console, AWS CLI, or `eksctl`.

## Identity & Permissions

### OIDC / IRSA (Legacy)
- Uses OpenID Connect to map Kubernetes service accounts to AWS IAM roles.
- Trust policies must reference the cluster OIDC provider URL.
- This setup can be complex due to explicit trust policy requirements.

### EKS Pod Identity (Modern)
- A Pod Identity Agent runs as a daemonset on worker nodes.
- It intercepts AWS credential requests and provides the correct IAM role.
- This approach can be simpler across multiple clusters because it avoids per-cluster trust policy changes.

### Critical Trust Policy
- For Pod Identity to work, the IAM role trust policy must allow the service principal `sts.amazonaws.com` or the required AWS identity provider.
- The trust policy must explicitly permit the correct service to assume the role.

## Triage & Troubleshooting Steps

### Check Status
- Use `kubectl get pods --all-namespaces` to find pods in `Pending`, `CrashLoopBackOff`, or `Error` states.

### Inspect Events
- Run `kubectl describe pod <name> -n <namespace>`.
- Scroll to the `Events` section to identify scheduling or volume mount failures.

### Analyze Logs
- Use `kubectl logs <pod-name> -n <namespace>` for current container output.
- If the pod crashed immediately, use `kubectl logs <pod-name> -n <namespace> --previous`.

### Verify Storage
- Use `kubectl get pvc --all-namespaces` to check PVC states.
- Ensure volumes are `Bound` and the storage class is available.

### Address Constraints
- `Insufficient cpu/memory` usually means node resources are exhausted.
- `Too many pods` can mean the EC2 instance type has reached its ENI/IP limit.
- Scale node groups or choose instance types with higher pod density.

## Key Error Resolutions

### 403 Unauthorized
- Often caused by a missing IAM role trust policy.
- Check that the role is permitted to assume the necessary AWS identity provider.
- Ensure Pod Identity is configured and associated correctly.

### Pending Pods
- Commonly caused by reaching the physical pod limit of the EC2 instance type.
- Also may be caused by insufficient node resources or scheduling constraints.

### CrashLoopBackOff
- Usually due to application startup failures.
- Common causes include misconfigured environment variables, missing secrets, or failing readiness/liveness probes.

## Summary
- Ingress provides Layer 7 routing while Service LoadBalancer operates at Layer 4.
- ALB on EKS requires the AWS Load Balancer Controller and proper annotations.
- EBS CSI driver is the standard persistent storage solution for EKS.
- Identity and permissions are critical: IRSA and Pod Identity are different approaches with distinct trust models.
- Use pod status, events, logs, and PVC checks to isolate issues quickly.
