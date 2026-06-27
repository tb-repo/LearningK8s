# Session 08: RBAC And Service Account Permissions

This session introduces Kubernetes Role-Based Access Control.

The main teaching idea is:

```text
Authentication answers: who are you?
Authorization answers: what are you allowed to do?
RBAC answers authorization with Roles, ClusterRoles, RoleBindings, and ClusterRoleBindings.
```

In this session, students create ServiceAccounts, prove that they have no useful permissions by default, then grant least-privilege access one step at a time.

## RBAC Building Blocks

| Object | Scope | Main use |
| --- | --- | --- |
| ServiceAccount | Namespace | Identity used by Pods and automation inside Kubernetes |
| Role | Namespace | Permissions for namespaced resources in one Namespace |
| RoleBinding | Namespace | Connects a user, group, or ServiceAccount to a Role or ClusterRole in one Namespace |
| ClusterRole | Cluster | Reusable permission set, or permissions for cluster-scoped resources |
| ClusterRoleBinding | Cluster | Connects a subject to a ClusterRole across the whole cluster |

## Important Mental Model

```text
Subject
  -> ServiceAccount, user, or group
    -> bound by RoleBinding or ClusterRoleBinding
      -> to Role or ClusterRole
        -> which allows verbs on resources
```

Example:

```text
system:serviceaccount:rbac-lab:dev-reader
  -> RoleBinding in rbac-lab
    -> Role named pod-reader
      -> can get/list/watch Pods in rbac-lab
```

## RBAC Is Not EKS IAM

On EKS, there are two permission systems that often appear together:

- AWS IAM controls access to AWS APIs.
- Kubernetes RBAC controls access to the Kubernetes API.

IAM Roles for Service Accounts can let a Pod call AWS services. RBAC lets that
same Pod call Kubernetes resources such as Pods, Services, ConfigMaps, Nodes,
and Deployments.

## Sub-Session Order

Follow the sub-sessions in this order:

1. `subsessions/01-prerequisites-and-namespace`: create the RBAC lab Namespace.
2. `subsessions/02-service-accounts-and-deny-by-default`: create identities and inspect default denial.
3. `subsessions/03-namespace-role-and-rolebinding`: grant namespaced read access with a Role.
4. `subsessions/04-clusterrole-with-rolebinding`: reuse a ClusterRole inside one Namespace.
5. `subsessions/05-clusterrolebinding-for-cluster-scope`: grant cluster-scoped read access carefully.

## Prerequisites

You need:

- A working Kubernetes cluster.
- `kubectl` configured.
- A current identity with permission to create RBAC objects.
- Permission to impersonate ServiceAccounts for `kubectl auth can-i --as=...`
  checks. A cluster-admin style training identity normally has this.

Check the current cluster and your own permissions:

```bash
kubectl version
kubectl get nodes
kubectl auth can-i create roles -n default
kubectl auth can-i create clusterroles
kubectl auth can-i impersonate serviceaccounts
```

## Target Shape By The End

```text
rbac-lab Namespace

ServiceAccounts:
  dev-reader
  app-auditor
  platform-viewer

Role:
  pod-reader
    -> read Pods, Pod logs, and Deployments in rbac-lab

RoleBinding:
  dev-reader-pod-reader
    -> grants dev-reader the pod-reader Role in rbac-lab

ClusterRole:
  workload-viewer
    -> read common namespaced workload resources

RoleBinding:
  app-auditor-workload-viewer
    -> grants app-auditor workload-viewer only in rbac-lab

ClusterRole:
  node-reader
    -> read Nodes

ClusterRoleBinding:
  platform-viewer-node-reader
    -> grants platform-viewer node read access across the cluster
```

## Full Apply Order

From `sessions/08-rbac`:

```bash
kubectl apply -f subsessions/01-prerequisites-and-namespace/
kubectl apply -f subsessions/02-service-accounts-and-deny-by-default/
kubectl apply -f subsessions/03-namespace-role-and-rolebinding/
kubectl apply -f subsessions/04-clusterrole-with-rolebinding/
kubectl apply -f subsessions/05-clusterrolebinding-for-cluster-scope/
```

Set useful identity variables:

```bash
DEV_READER=system:serviceaccount:rbac-lab:dev-reader
APP_AUDITOR=system:serviceaccount:rbac-lab:app-auditor
PLATFORM_VIEWER=system:serviceaccount:rbac-lab:platform-viewer
```

Check the final permissions:

```bash
kubectl auth can-i list pods -n rbac-lab --as="$DEV_READER"
kubectl auth can-i delete pods -n rbac-lab --as="$DEV_READER"

kubectl auth can-i list services -n rbac-lab --as="$APP_AUDITOR"
kubectl auth can-i list services -n default --as="$APP_AUDITOR"

kubectl auth can-i list nodes --as="$PLATFORM_VIEWER"
kubectl auth can-i list pods --all-namespaces --as="$PLATFORM_VIEWER"
```

Expected pattern:

```text
dev-reader:      can read selected objects in rbac-lab, cannot delete them.
app-auditor:     can read selected namespaced resources only in rbac-lab.
platform-viewer: can read Nodes, but not Pods across all Namespaces.
```

## Cleanup

From `sessions/08-rbac`:

```bash
kubectl delete -f subsessions/05-clusterrolebinding-for-cluster-scope/ --ignore-not-found
kubectl delete -f subsessions/04-clusterrole-with-rolebinding/ --ignore-not-found
kubectl delete -f subsessions/03-namespace-role-and-rolebinding/ --ignore-not-found
kubectl delete -f subsessions/02-service-accounts-and-deny-by-default/ --ignore-not-found
kubectl delete -f subsessions/01-prerequisites-and-namespace/ --ignore-not-found
```

## Review Questions

1. What is the difference between authentication and authorization?
ANS: Authentication vs. AuthorizationAuthentication (AuthN) verifies who you are (identity).Authorization (AuthZ) determines what you can do (permissions).
2. Why should most application Pods use a dedicated ServiceAccount?
ANS:Dedicated ServiceAccounts for Pods
Isolation: Prevents one compromised Pod from accessing other resources.
Least Privilege: Limits permissions strictly to what that specific application needs.
Auditability: Makes tracking actions in logs easier by separating identities.
3. What is the difference between a Role and a ClusterRole?
ANS: Role vs. ClusterRoleRole: Namespaced resource. Grants access within a specific Namespace only.
ClusterRole: Cluster-scoped resource. Grants access across all Namespaces or to cluster-wide resources (like Nodes).
4. What is the difference between a RoleBinding and a ClusterRoleBinding?
ANS: RoleBinding vs. ClusterRoleBindingRoleBinding: Assigns permissions (from a Role or ClusterRole) within a specific Namespace.
ClusterRoleBinding: Assigns permissions cluster-wide across all Namespaces.
5. Why does a RoleBinding to a ClusterRole still only grant access in one Namespace?
ANS: RoleBinding to a ClusterRole ScopeBinding Context: 
The RoleBinding object itself is bound to a specific Namespace.Namespace Limitation: It applies the ClusterRole's permissions only within that binding's Namespace.
Efficiency: Reuses common permission templates without duplicating Roles in every Namespace.
6. Why is granting `get`, `list`, and `watch` safer than granting `*`?
ANS: Specific Verbs vs. Wildcards (*)Least Privilege: 
Wildcards grant powerful administrative actions like delete and update.
Risk Reduction: get, list, and watch only allow reading data.Blast Radius: Prevents accidental or malicious modification and deletion of resources.
7. Why should access to Secrets be treated carefully?
ANS: Protecting SecretsSensitive Data: 
Secrets hold passwords, private keys, and API tokens.
Privilege Escalation: Access to Secrets can allow attackers to impersonate admin users.
External Risk: Compromised tokens can expose connected cloud infrastructure and databases.
8. Why should ClusterRoleBindings be reviewed more carefully than RoleBindings?
ANS: Reviewing ClusterRoleBindings Carefully
Cluster-Wide Impact: They grant permissions across the entire cluster.
Data Exposure: A single mistake can expose sensitive data in all current and future Namespaces.No Boundaries: They bypass the logical isolation provided by Namespaces. 
9. In EKS, what is the difference between Kubernetes RBAC and AWS IAM?
ANS:Kubernetes RBAC vs. AWS IAM in EKS
Kubernetes RBAC: Controls actions inside the cluster (e.g., creating Pods, reading ConfigMaps).
AWS IAM: Controls actions outside the cluster (e.g., creating EC2 instances, accessing ECR registries).

## References

- Kubernetes RBAC documentation: `https://kubernetes.io/docs/reference/access-authn-authz/rbac/`
- Kubernetes ServiceAccount documentation: `https://kubernetes.io/docs/concepts/security/service-accounts/`
- Kubernetes authorization overview: `https://kubernetes.io/docs/reference/access-authn-authz/authorization/`
- Kubernetes `kubectl auth can-i`: `https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/`
