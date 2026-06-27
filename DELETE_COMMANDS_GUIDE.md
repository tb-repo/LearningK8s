# Kubernetes Delete Commands Guide

Comprehensive reference for deleting Kubernetes resources with their purposes.

---

## Table of Contents

1. [Ingress Controllers](#ingress-controllers)
2. [Ingress Resources](#ingress-resources)
3. [Deployments & Pods](#deployments--pods)
4. [Services](#services)
5. [Namespaces](#namespaces)
6. [Storage Resources](#storage-resources)
7. [Configuration & Secrets](#configuration--secrets)
8. [Custom Resources](#custom-resources)
9. [Helm Releases](#helm-releases)
10. [Bulk Delete Operations](#bulk-delete-operations)

---

## Ingress Controllers

### Delete Helm-Installed Ingress Controller

```bash
# For F5 NGINX Ingress Controller
helm uninstall f5-nginx-ingress -n nginx-ingress

# For any Helm-installed controller (list first to find release name)
helm list -n nginx-ingress
helm uninstall <release-name> -n <namespace>
```

**Purpose:** Removes the ingress controller deployment, services, and associated resources installed via Helm.

### Delete Manually-Installed Ingress Controller

```bash
# Delete by manifest file
kubectl delete -f ingress-controller-manifest.yaml

# Delete specific deployment
kubectl delete deployment -n nginx-ingress f5-nginx-ingress-controller
```

**Purpose:** Removes ingress controller resources created with manual YAML manifests.

### Delete Ingress Controller Namespace

```bash
kubectl delete namespace nginx-ingress
```

**Purpose:** Deletes the entire namespace and all resources within it (ingress controller, RBAC, ConfigMaps, etc.).

### Delete Ingress Controller RBAC

```bash
# Delete ClusterRole
kubectl delete clusterrole nginx-ingress

# Delete ClusterRoleBinding
kubectl delete clusterrolebinding nginx-ingress

# Delete Role in namespace
kubectl delete role -n nginx-ingress nginx-ingress

# Delete RoleBinding in namespace
kubectl delete rolebinding -n nginx-ingress nginx-ingress
```

**Purpose:** Removes Role-Based Access Control resources associated with the ingress controller.

### Delete Ingress Controller Custom Resource Definitions

```bash
# Delete NGINX ingress CRDs
kubectl delete crd virtualservers.k8s.nginx.org
kubectl delete crd virtualserverroutes.k8s.nginx.org
kubectl delete crd transportservers.k8s.nginx.org
kubectl delete crd policies.k8s.nginx.org
kubectl delete crd globalconfigurations.k8s.nginx.org

# Delete IngressClass
kubectl delete ingressclass nginx
```

**Purpose:** Removes custom resource definitions and ingress classes used by the controller.

---

## Ingress Resources

### Delete Specific Ingress

```bash
# Delete single ingress in namespace
kubectl delete ingress message-board-ingress-f5-nginx -n tb-app-ingress

# Delete all ingresses in namespace
kubectl delete ingress --all -n tb-app-ingress
```

**Purpose:** Removes Ingress resources that route traffic to services.

### Delete Ingress by Label

```bash
# Delete ingresses with specific label
kubectl delete ingress -l app=message-board -n tb-app-ingress
```

**Purpose:** Removes Ingress resources matching specific labels (useful for bulk deletion).

---

## Deployments & Pods

### Delete Deployment

```bash
# Delete specific deployment
kubectl delete deployment frontend -n tb-app-ingress

# Delete all deployments in namespace
kubectl delete deployments --all -n tb-app-ingress
```

**Purpose:** Removes deployment and its associated pods/replicas.

### Delete StatefulSet

```bash
# Delete StatefulSet (pods are deleted sequentially)
kubectl delete statefulset postgres -n tb-app-ingress

# Delete StatefulSet and associated persistent volumes
kubectl delete statefulset postgres --cascade=foreground -n tb-app-ingress
```

**Purpose:** Removes StatefulSet resources (typically for databases).

### Delete DaemonSet

```bash
kubectl delete daemonset <daemonset-name> -n <namespace>
```

**Purpose:** Removes DaemonSet that runs on every node.

### Delete Pod Directly

```bash
# Delete single pod
kubectl delete pod <pod-name> -n <namespace>

# Force delete pod (immediate termination)
kubectl delete pod <pod-name> -n <namespace> --grace-period=0 --force
```

**Purpose:** Removes individual pods (useful for testing or debugging).

### Delete Pods by Label

```bash
kubectl delete pods -l app=frontend -n tb-app-ingress
```

**Purpose:** Deletes all pods matching a specific label.

---

## Services

### Delete Service

```bash
# Delete specific service
kubectl delete service frontend -n tb-app-ingress

# Delete all services in namespace
kubectl delete services --all -n tb-app-ingress
```

**Purpose:** Removes Service (load balancer, ClusterIP, NodePort, etc.).

### Delete LoadBalancer Service (AWS)

```bash
kubectl delete service nginx-ingress-controller -n nginx-ingress
```

**Purpose:** Removes LoadBalancer service and associated AWS load balancer resource.

---

## Namespaces

### Delete Entire Namespace

```bash
# Standard delete
kubectl delete namespace tb-app-ingress

# Force delete namespace (use with caution)
kubectl delete namespace tb-app-ingress --grace-period=0 --force
```

**Purpose:** Deletes namespace and ALL resources within it (irreversible).

### Delete Multiple Namespaces

```bash
kubectl delete namespaces nginx-ingress tb-app-ingress app-storage
```

**Purpose:** Removes multiple namespaces in one command.

---

## Storage Resources

### Delete Persistent Volume Claim (PVC)

```bash
# Delete specific PVC
kubectl delete pvc postgres-pvc -n tb-app-ingress

# Delete all PVCs in namespace
kubectl delete pvc --all -n tb-app-ingress
```

**Purpose:** Removes persistent volume claim (data may be retained based on reclaim policy).

### Delete Persistent Volume (PV)

```bash
# Delete specific PV
kubectl delete pv postgres-pv

# Delete all PVs
kubectl delete pv --all
```

**Purpose:** Removes persistent volume (note: PVs are cluster-scoped, not namespaced).

### Delete StorageClass

```bash
kubectl delete storageclass fast-storage
```

**Purpose:** Removes storage class used for dynamic provisioning.

### Delete with Data Cleanup

```bash
# Delete PVC and force immediate cleanup
kubectl patch pvc postgres-pvc -n tb-app-ingress -p '{"metadata":{"finalizers":null}}'
kubectl delete pvc postgres-pvc -n tb-app-ingress

# Delete PV and retain data
kubectl patch pv postgres-pv -p '{"metadata":{"finalizers":null}}'
kubectl delete pv postgres-pv
```

**Purpose:** Removes storage resources and handles finalizers that may block deletion.

---

## Configuration & Secrets

### Delete ConfigMap

```bash
# Delete specific ConfigMap
kubectl delete configmap app-config -n tb-app-ingress

# Delete all ConfigMaps in namespace
kubectl delete configmaps --all -n tb-app-ingress
```

**Purpose:** Removes ConfigMap containing application configuration data.

### Delete Secret

```bash
# Delete specific secret
kubectl delete secret database-credentials -n tb-app-ingress

# Delete all secrets in namespace
kubectl delete secrets --all -n tb-app-ingress
```

**Purpose:** Removes Secret containing sensitive data (passwords, tokens, certificates).

### Delete ConfigMap/Secret by Label

```bash
kubectl delete configmap -l environment=production -n tb-app-ingress
kubectl delete secret -l type=database -n tb-app-ingress
```

**Purpose:** Removes configuration/secrets matching specific labels.

---

## Custom Resources

### Delete VirtualServer (NGINX)

```bash
kubectl delete virtualserver message-board-vs -n tb-app-ingress
```

**Purpose:** Removes NGINX VirtualServer custom resource (advanced routing).

### Delete Policy

```bash
kubectl delete policy rate-limit-policy -n tb-app-ingress
```

**Purpose:** Removes policy custom resource affecting ingress behavior.

### Delete All Custom Resources of Type

```bash
kubectl delete virtualservers --all -n tb-app-ingress
kubectl delete policies --all -n tb-app-ingress
```

**Purpose:** Removes all custom resources of a specific type.

---

## Helm Releases

### Delete Helm Release

```bash
# Standard delete (resources remain)
helm uninstall <release-name> -n <namespace>

# Delete release with all resources
helm uninstall <release-name> -n <namespace> --cascade=foreground
```

**Purpose:** Removes Helm release and associated resources.

### Delete All Helm Releases in Namespace

```bash
# Get all releases
helm list -n <namespace>

# Uninstall each release
helm uninstall <release-1> <release-2> -n <namespace>
```

**Purpose:** Removes multiple Helm releases at once.

### Force Delete Helm Release

```bash
# Delete without waiting for resource cleanup
helm uninstall <release-name> -n <namespace> --no-hooks
```

**Purpose:** Removes Helm release immediately without running pre-delete hooks.

---

## Bulk Delete Operations

### Delete All Resources in Namespace

```bash
# Delete all non-system resources in namespace
kubectl delete all --all -n tb-app-ingress

# This deletes: pods, services, deployments, daemonsets, statefulsets, jobs, ingresses
# But NOT: namespaces, storage, RBAC, custom resources
```

**Purpose:** Quick cleanup of most resources in a namespace.

### Delete Everything Including Storage

```bash
# Delete all resources including PVCs, Secrets, ConfigMaps
kubectl delete all,pvc,secrets,configmap --all -n tb-app-ingress
```

**Purpose:** Complete cleanup of a namespace with all resource types.

### Delete by Namespace Label

```bash
# List namespaces with label
kubectl get namespaces -l environment=test

# Delete namespaces matching label
kubectl delete namespace -l environment=test
```

**Purpose:** Removes all namespaces matching a label selector.

### Delete All Resources Matching Label

```bash
# Delete all resources with specific label
kubectl delete all -l app=frontend -n tb-app-ingress

# Delete across all namespaces
kubectl delete all -l app=frontend --all-namespaces
```

**Purpose:** Removes all resources associated with a specific application or component.

### Delete with Age/Time-based Selection

```bash
# No direct kubectl support, but can use jq
kubectl get pods -n tb-app-ingress -o json | \
  jq -r '.items[] | select(.metadata.creationTimestamp < "2025-01-01T00:00:00Z") | .metadata.name' | \
  xargs -I {} kubectl delete pod {} -n tb-app-ingress
```

**Purpose:** Removes resources created before a specific date.

---

## Special Deletion Scenarios

### Delete Stuck/Pending Resources

```bash
# Remove finalizers forcing deletion
kubectl patch <resource-type> <resource-name> -n <namespace> \
  -p '{"metadata":{"finalizers":null}}' --type merge

# Then delete the resource
kubectl delete <resource-type> <resource-name> -n <namespace>
```

**Purpose:** Removes resources blocked by finalizers (dangling resources).

### Delete with Cascade Policy

```bash
# Delete and cascade (orphan=false): Delete resource and dependent resources
kubectl delete deployment frontend -n tb-app-ingress --cascade=background

# Delete without cascading: Resource deleted but dependents remain
kubectl delete deployment frontend -n tb-app-ingress --cascade=orphan
```

**Purpose:** Controls how dependent resources are handled during deletion.

### Dry Run: Preview What Will Be Deleted

```bash
# See what would be deleted without actually deleting
kubectl delete ingress --all -n tb-app-ingress --dry-run=client

# See server-side preview
kubectl delete ingress --all -n tb-app-ingress --dry-run=server
```

**Purpose:** Safely preview deletion without making changes.

---

## Common Cleanup Sequences

### Clean Up F5 NGINX Lab

```bash
# 1. Delete ingress resources
kubectl delete ingress --all -n tb-app-ingress --ignore-not-found

# 2. Uninstall Helm release
helm uninstall f5-nginx-ingress -n nginx-ingress

# 3. Delete ingress namespace
kubectl delete namespace nginx-ingress --ignore-not-found

# 4. Delete app namespace (optional)
kubectl delete namespace tb-app-ingress --ignore-not-found
```

### Full Cluster Cleanup

```bash
# 1. List all namespaces
kubectl get namespaces

# 2. Delete non-system namespaces
kubectl delete namespace tb-app-ingress nginx-ingress --ignore-not-found

# 3. Verify cleanup
kubectl get namespaces
kubectl get all --all-namespaces
```

### Cleanup Persistent Data

```bash
# 1. Delete all PVCs
kubectl delete pvc --all -n tb-app-ingress

# 2. Delete all PVs
kubectl delete pv --all

# 3. Verify deletion
kubectl get pvc --all-namespaces
kubectl get pv
```

---

## Safe Deletion Practices

1. **Always use `--dry-run=client` first** to preview changes
2. **Use `--ignore-not-found`** to prevent errors if resource doesn't exist
3. **Use namespaces** to isolate deletions and prevent accidents
4. **Label resources** for selective deletion
5. **Backup data** before deleting PVCs or Secrets
6. **Use `kubectl get`** to verify resource state before deletion
7. **Document deletion commands** in runbooks for team consistency

---

## Quick Reference

| Task | Command |
|------|---------|
| Delete ingress controller (Helm) | `helm uninstall <release> -n <ns>` |
| Delete all ingresses | `kubectl delete ingress --all -n <ns>` |
| Delete all pods | `kubectl delete pod --all -n <ns>` |
| Delete namespace | `kubectl delete namespace <name>` |
| Delete deployment | `kubectl delete deployment <name> -n <ns>` |
| Delete service | `kubectl delete service <name> -n <ns>` |
| Delete PVC | `kubectl delete pvc <name> -n <ns>` |
| Delete secret | `kubectl delete secret <name> -n <ns>` |
| Delete ConfigMap | `kubectl delete configmap <name> -n <ns>` |
| Delete by label | `kubectl delete <resource> -l <label> -n <ns>` |
| Dry run preview | `kubectl delete <resource> <name> --dry-run=client` |
| Force delete | `kubectl delete <resource> <name> --grace-period=0 --force` |

---

## References

- [Kubernetes Delete Documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_delete/)
- [Managing Resources in Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/manage-deployment/)
- [Cascading Deletion Policy](https://kubernetes.io/docs/concepts/architecture/garbage-collection/)
