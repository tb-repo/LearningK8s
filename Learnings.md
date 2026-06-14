## Summary of Work Completed

1. Kubernetes Storage Learning Path Review
Reviewed the 02-storage-pv-pvc-statefulset folder structure (6 subsessions)
Explained each YAML file's purpose step-by-step:
Namespace, ConfigMap, and Secret setup
Static PV and PVC creation
Postgres Deployment and Service with static storage
Flask Deployment and LoadBalancer Service
AWS StorageClass (ebs-gp3) for dynamic provisioning
PostgreSQL StatefulSet with dynamic PVC

2. Kubernetes Labels and Service Routing
Explained how pod labels (spec.template.metadata.labels) link to service selectors
Clarified that Services find pods through matching label selectors, not direct Deployment references

3. Docker Image Architecture Mismatch Issue
Diagnosed ErrImagePull / ImagePullBackOff errors
Root cause: Used t4g.small (Graviton/ARM64) node but image was only built for amd64
Error: no match for platform in manifest: not found
Solution: Use t3.small (amd64) node type instead

4. Created EKS Cluster Configuration File
Created cluster.yaml with:
OIDC enabled (iam.withOIDC: true)
IAM service accounts for EBS CSI driver and ALB controller
Managed addons: vpc-cni, coredns, kube-proxy, aws-ebs-csi-driver
Node group configuration (t3.small, 2-3 nodes)

5. Fixed EBS CSI Driver IAM Permissions
Problem: EBS CSI controller pods crashing with UnauthorizedOperation errors
Cause: Service account existed but lacked IAM role annotation
Solution:
Result: Restarted deployment → pods became healthy → StatefulSet PVC moved from Pending to Bound

6. Explained Headless Service Design
Clarified why postgres-headless has ClusterIP: None
Required for StatefulSets to provide stable Pod identity and DNS names
Allows inter-pod communication without load balancing

7. Diagnosed Database Schema Issue
Symptom: Flask showing "database is unavailable" error
Debugging: Checked Flask logs → found UndefinedTable: relation "messages" does not exist
Root cause: The messages table was never created (schema initialization failed during Flask startup)

Why: Postgres wasn't ready when Flask app started, so ensure_schema() function failed silently
Key learning: Always read detailed error logs, not just user-facing messages
Current State
✅ EKS cluster created with proper addons and IAM roles
✅ EBS CSI driver functional and provisioning volumes
✅ PostgreSQL StatefulSet running with dynamic storage (1Gi EBS volume)
✅ Flask app running and connecting to Postgres
❌ Database schema needs to be initialized (messages table missing)