# Argo CD Key Points

## 1. What this lab teaches

In this lab, Argo CD is installed using the official upstream manifests. That means students will use the standard Argo CD deployment package instead of a custom installation method like Helm or an operator. The purpose is to keep the setup simple so the focus stays on GitOps workflows.

The lab also avoids asking students to write Argo CD `Application` YAML files by hand. Instead, applications are created through the Argo CD web UI in a later session, making the learning experience easier and more visual.

## 2. What Argo CD installs in Kubernetes

Argo CD is composed of multiple Kubernetes resources working together:

- **Controllers**: continuously compare Git state with live cluster state.
- **API service**: provides the Argo CD web UI and REST API.
- **CRDs**: extend Kubernetes with Argo CD-specific resource types.
- **RBAC**: permissions that control who can do what inside Argo CD.

Using the official manifests deploys all of these components in a tested and supported configuration.

## 3. How Argo CD runs

Argo CD does not create its own Kubernetes control plane. It runs as ordinary Pods inside an existing cluster, usually in the `argocd` namespace.

The main Argo CD pods are:

- `argocd-server`: serves the UI and API.
- `argocd-repo-server`: clones Git repositories and generates manifests.
- `argocd-application-controller`: reconciles desired state from Git with live cluster state.
- `argocd-redis`: provides caching to improve performance.

These pods use the existing Kubernetes API server rather than creating new control plane components like `kube-apiserver` or `etcd`.

## 4. How Argo CD connects to target clusters

When Argo CD runs in a management cluster (the **Hub**), it can manage other clusters (the **Spokes**) by connecting to their Kubernetes API servers over TLS.

This means:

- The management cluster holds credentials for each target cluster.
- Argo CD uses HTTPS to talk to the target cluster API.
- No Argo CD software is required inside the target cluster for standard cluster registration.
- The target cluster must allow inbound API access from the management cluster.

## 5. Registering a target cluster

The common registration method is the Argo CD CLI:

```bash
argocd cluster add my-external-prod-cluster-context
```

That command does the following automatically:

1. Authenticates to the target cluster using your current `kubectl` context.
2. Creates a service account named `argocd-manager` in the target cluster.
3. Binds that service account to a role with deploy permissions.
4. Generates a secure token and certificate.
5. Stores those credentials as a Kubernetes Secret in the Argo CD namespace on the Hub.

After registration, Argo CD can securely deploy applications into the target cluster.

## 6. Where Argo CD stores cluster credentials

Argo CD stores target cluster connection details in secrets labeled with:

```yaml
argocd.argoproj.io/secret-type: cluster
```

These secrets contain:

- the target cluster name
- the API server URL
- authentication tokens
- TLS certificate data

These secrets allow the Argo CD controller to connect to each target cluster.

## 7. Network and security requirements

For secure production use, the Hub must be able to reach the target cluster API server over a private network.

Best practices include:

- Use private networking such as VPC peering, VNet peering, or transit gateways.
- Restrict access to the target API server port (`443` or `6443`) to only the Hub.
- Avoid exposing the target cluster API publicly.
- If direct connectivity is not possible, use a secure proxy or tunnel solution.

## 8. How Argo CD authenticates to target clusters

The target cluster uses a dedicated service account for Argo CD. That service account is often called `argocd-manager`.

The target cluster also needs a role binding that grants Argo CD permission to deploy resources. In simple demos this may be a `ClusterRoleBinding` to `cluster-admin`, but production deployments should use least privilege.

This means:

- Argo CD has a clear identity in the target cluster.
- It authenticates using a token stored on the Hub.
- It is authorized by Kubernetes RBAC on the target cluster.

## 9. Customizing Argo CD settings

Argo CD configuration is stored in Kubernetes objects rather than local config files.

The two main config objects are:

- `argocd-cm`: controls system settings and feature options.
- `argocd-rbac-cm`: defines Argo CD access control policies.

For example, `argocd-cm` can set UI banners or exclude certain resources from tracking, while `argocd-rbac-cm` maps external teams to Argo CD roles.

## 10. Performance tuning

If Argo CD needs to handle a heavier workload, you can tune it with settings such as:

- `ARGOCD_RECONCILIATION_TIMEOUT`: how often Argo CD checks Git.
- `--status-processors`: how many application statuses Argo CD can process in parallel.

You can also adjust Pod resource requests and limits for components like the application controller and repo server.

## 11. Summary

Argo CD is a GitOps controller that runs inside a Kubernetes cluster and manages applications by syncing Git state to live clusters.

Key takeaways:

- Argo CD uses the existing Kubernetes control plane.
- It runs as Pods in the `argocd` namespace.
- It connects to target clusters using secure kubeconfig secrets.
- The `argocd cluster add` command automates target cluster registration.
- Network access and RBAC are the main requirements for clustered deployments.

This version of the file is streamlined for readability and should help make the architecture and workflow easier to understand.
