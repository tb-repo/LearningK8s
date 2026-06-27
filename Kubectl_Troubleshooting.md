# Kubernetes Triage & Troubleshooting Playbook

When workloads are stuck or failing in a cluster, follow this sequential debugging ladder to isolate and fix the root cause.

---

## Phase 1: High-Level Cluster Assessment

Before inspecting applications, verify that the underlying cluster infrastructure is healthy and has enough capacity.

### Step 1: Check node status and capacity

Verify whether worker nodes are Ready and whether they are overloaded.

```bash
kubectl get nodes
kubectl top nodes
kubectl describe nodes | grep -E "Name:|Resource|Requests|Limits|Pods:"
```

### Step 2: Check system component health

Confirm that core cluster services such as DNS, networking, and storage controllers are running.

```bash
kubectl get pods -n kube-system
kubectl get pods -n ingress-nginx
```

Inspect controller logs when needed:

```bash
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller --tail=100
```

---

## Phase 2: Application Triage (Pod Lifecycle)

Isolate workload problems by checking pod status, events, and container logs.

### Step 3: Identify stuck workloads

List pods across namespaces to detect failures or abnormal statuses.

```bash
kubectl get pods --all-namespaces
kubectl get pods -n <namespace-name> -w
```

### Step 4: Debug Pending pods (scheduling layer)

A pod in `Pending` has not been scheduled. This is a cluster scheduling or capacity issue.

```bash
kubectl describe pod <pod-name> -n <namespace-name>
```

What to look for in the `Events:` section:

- `Insufficient cpu/memory` → worker nodes are full. Scale the node group.
- `Too many pods` → AWS ENI/IP pod limit reached for the instance type. Add nodes or use larger instance sizes.
- `waiting for a volume to be created` → move to Phase 3 for storage troubleshooting.

### Step 5: Debug `CrashLoopBackOff` / Error pods (application layer)

If a pod is running but its container is repeatedly failing, the scheduler succeeded and the runtime is the issue.

```bash
kubectl logs <pod-name> -n <namespace-name>
kubectl logs <pod-name> -n <namespace-name> --previous
kubectl logs <pod-name> -c <container-name> -n <namespace-name>
```

Use the `--previous` option when the container crashes immediately after startup.

---

## Phase 3: Storage Triage (Stateful Layer)

If databases or stateful apps fail to initialize, inspect persistent volume claims and provisioners.

### Step 6: Verify persistent volume chains

```bash
kubectl get storageclass
kubectl get pvc --all-namespaces
```

Triage rules:

- If PVC is `Bound` → storage was provisioned successfully.
- If PVC is `Pending` → inspect the PVC and the storage backend.

```bash
kubectl describe pvc <pvc-name> -n <namespace-name>
```

Check for errors related to CSI drivers, IAM permissions, provisioner failures, or missing cloud volumes.

---

## Phase 4: Network & Ingress Triage (Routing Layer)

If pods are `Running` but traffic does not reach them, audit the networking and ingress path.

### Step 7: Inspect Ingress and service mapping

```bash
kubectl get ingress --all-namespaces
kubectl describe ingress <ingress-name> -n <namespace-name>
kubectl get service --all-namespaces
```

Validate that:

- the Ingress has an external IP or DNS assigned
- backend services are healthy
- target service ports match your application

---

## Phase 5: Fast Recovery Commands (Emergency Operations)

### Force-delete unresponsive pods

If a pod is stuck terminating:

```bash
kubectl delete pod <pod-name> -n <namespace-name> --grace-period=0 --force
```

### Clear a stuck namespace

If a namespace refuses to terminate due to stuck finalizers:

```bash
kubectl delete namespace <namespace-name> --now
```

### Restart a deployment quickly

Force pods to restart without changing manifests:

```bash
kubectl rollout restart deployment/<deployment-name> -n <namespace-name>
```

---

## Troubleshooting checklist

Use this sequence when debugging cluster issues:

1. Verify node health and capacity.
2. Confirm system pods and controllers are healthy.
3. Find failing pods and inspect events.
4. Diagnose scheduling vs runtime failures.
5. Validate storage provisioning and PVC states.
6. Check ingress, services, and network routing.
7. Use recovery commands only after the root cause is identified.
