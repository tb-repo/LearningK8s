# Session 02: Persistent Storage, PV/PVC, StorageClass, And StatefulSet

This session continues the same Flask/PostgreSQL sample app from Session 01, but focuses on persistent storage.

App image:

```text
prashantdey/appk8stutorial:1.0
```

The key teaching idea is:

```text
Flask is stateless -> Deployment
PostgreSQL is stateful -> persistent storage and StatefulSet
```

## Sub-Session Order

Follow the sub-sessions in this order:

1. `subsessions/01-storage-problem-and-shared-config`: explain the storage problem and create Namespace, ConfigMap, and Secret.
2. `subsessions/02-static-pv-pvc`: create a static `hostPath` PV and a PostgreSQL PVC.
3. `subsessions/03-postgres-with-static-pvc`: run PostgreSQL with the PVC and prove storage survives Pod replacement.
4. `subsessions/04-flask-with-persistent-db`: connect the Flask 
app to the persistent PostgreSQL database.

Before moving to point 5 create the required role for the EKS to use EBS:

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
aws iam update-assume-role-policy --role-name TB_EKS_EBS_CSI_DriverRole --policy-document file://trust-policy.json
```

```bash
eksctl create podidentityassociation `
  --cluster=tb-k8s-cluster-1 `
  --region=ap-south-1 `
  --namespace=kube-system `
  --service-account-name=ebs-csi-controller-sa `
  --role-arn=arn:aws:iam::386346184566:role/TB_EKS_EBS_CSI_DriverRole
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

## Full Static PV/PVC Apply Order

From `sessions/02-storage-pv-pvc-statefulset`:

```bash
kubectl apply -f subsessions/01-storage-problem-and-shared-config/
kubectl apply -f subsessions/02-static-pv-pvc/
kubectl apply -f subsessions/03-postgres-with-static-pvc/
kubectl apply -f subsessions/04-flask-with-persistent-db/
```

## Full StatefulSet Apply Order

For EKS dynamic storage:

```bash
kubectl apply -f subsessions/01-storage-problem-and-shared-config/
kubectl apply -f subsessions/05-storageclass/
kubectl apply -f subsessions/06-postgres-statefulset/
kubectl apply -f subsessions/04-flask-with-persistent-db/
```

If the cluster already has a suitable default StorageClass, you can still use the provided gp3 StorageClass for explicit teaching.

## Cleanup

From `sessions/02-storage-pv-pvc-statefulset`:

```bash
kubectl delete -f subsessions/04-flask-with-persistent-db/ --ignore-not-found
kubectl delete -f subsessions/06-postgres-statefulset/ --ignore-not-found
kubectl delete pvc -n app-storage -l app=postgres,storage-demo=stateful --ignore-not-found
kubectl delete -f subsessions/05-storageclass/ --ignore-not-found
kubectl delete -f subsessions/03-postgres-with-static-pvc/ --ignore-not-found
kubectl delete -f subsessions/02-static-pv-pvc/ --ignore-not-found
kubectl delete -f subsessions/01-storage-problem-and-shared-config/ --ignore-not-found
```

## Review Questions

1. Why does PostgreSQL need persistent storage?
2. What is the difference between a PV and a PVC?
3. Why is `hostPath` useful for learning but risky for production?
4. What does a StorageClass add?
5. Why does a StatefulSet fit PostgreSQL better than a normal Deployment?

## Review Answers

1. To persist database data across Pod restarts and node failures.
2. PV is a cluster storage resource; PVC is a Pod's claim/request that binds to a PV.
3. `hostPath` is simple and node-local for demos but not portable, durable, or secure in production.
4. StorageClass enables dynamic provisioning and selection of storage backends/parameters.
5. StatefulSet provides stable identities and stable persistent volume claims per replica.

