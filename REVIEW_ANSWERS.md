Consolidated Review Question Answers
=================================

This file collects answers to every "Review Questions" section found in the repository README files.

1) sessions/04-hpa-vpa/README.md
- Q1: What field does HPA change on a Deployment?
  A: `spec.replicas` (the desired replica count).
- Q2: Why does CPU-based HPA need CPU requests?
  A: To compute percent utilization relative to a known requested baseline.
- Q3: What happens if a Pod requests `100m` CPU and uses `100m` CPU?
  A: Utilization=100%; HPA may scale if target <100%; scheduler reserved that CPU.
- Q4: Why is HPA usually better for stateless web applications?
  A: They scale horizontally easily, share no local state, and tolerate replica churn.
- Q5: Why is VPA not built into Kubernetes by default?
  A: VPA is an add-on controller with eviction behavior and policy choices; it was kept optional due to complexity and potential disruption.
- Q6: What is the difference between VPA `Off` and `Recreate` modes?
  A: `Off` only records recommendations; `Recreate` evicts/recreates pods to apply new requests.
- Q7: Why can CPU-based HPA and CPU-changing VPA conflict on the same Deployment?
  A: VPA changes requests which alters HPA's utilization calculations; both controllers may fight over desired replica counts.
- Q8: When would you use VPA only for recommendations?
  A: When you want to review and apply resource changes manually or avoid automatic evictions alongside HPA.
- Q9: What must happen at the node layer if HPA creates more Pods than the cluster can schedule?
  A: New node capacity must be provisioned (manual, Cluster Autoscaler, Karpenter) or Pods stay Pending.

2) sessions/06-daemonsets/README.md
- Q1: What decides the number of Pods for a Deployment?
  A: The controller’s `spec.replicas` (or HPA updating it).
- Q2: What decides the number of Pods for a DaemonSet?
  A: The number of eligible Nodes matching the DaemonSet's node selector/affinity/taints.
- Q3: Why is a DaemonSet useful for log collection?
  A: It guarantees one log-collector agent runs on each Node where logs are produced locally.
- Q4: What happens to a DaemonSet when a new Node joins the cluster?
  A: Kubernetes creates one DaemonSet Pod on that new eligible Node.
- Q5: Why should a Deployment and DaemonSet not share the same selector?
  A: Shared selectors cause controller ownership conflicts and unpredictable pod management.
- Q6: If a cluster has four eligible Nodes, how many Pods should one DaemonSet create?
  A: Four Pods (one per eligible Node).
- Q7: Why is a Deployment better than a DaemonSet for a stateless web API?
  A: Deployments control replica counts, support rolling updates and scaling independent of node topology.

3) sessions/06-daemonsets/subsessions/03-deployment-and-daemonset-mix/README.md
- Q1: Which object controls the `mix-web` Pod count?
  A: The `Deployment` for `mix-web` (its `spec.replicas`).
- Q2: Which object controls the `mix-node-agent` Pod count?
  A: The `DaemonSet` for `mix-node-agent` (one per matching Node).
- Q3: Why does scaling the Deployment not change the DaemonSet?
  A: They are separate controllers with different responsibilities; scaling Deployment changes only its replica count.
- Q4: Why does the Service route only to the Deployment Pods?
  A: The Service's selector matches the Deployment Pod labels, not the DaemonSet labels.
- Q5: What could go wrong if both controllers used the same selector?
  A: Both controllers would try to manage the same Pods, causing ownership conflicts and erratic behavior.

4) sessions/06-daemonsets/subsessions/02-daemonset-basics/README.md
- Q1: Why does this object create one Pod per Node?
  A: The DaemonSet controller ensures one Pod is scheduled on each Node that matches its selection rules.
- Q2: What happens if you delete a DaemonSet Pod?
  A: The controller will recreate it on the same Node (unless Node is removed or selection changed).
- Q3: Why does a DaemonSet not have a `replicas` field?
  A: Its pod count is derived from Nodes, not a fixed replica target.
- Q4: How could you limit a DaemonSet to only selected Nodes?
  A: Use `nodeSelector`, node affinity or taints/tolerations to restrict matching Nodes.

5) sessions/04-hpa-vpa/subsessions/04-vpa-recommendations/README.md
(Answers already provided in the lesson; reproduced concisely)
- Q1: Why does VPA need Metrics Server?
  A: To read live container resource usage required to generate recommendations.
- Q2: What does VPA write into its status?
  A: Resource recommendations under `.status.recommendation` (lower/target/upper bounds).
- Q3: What is the difference between `Off` and `Recreate` mode?
  A: `Off` only suggests values; `Recreate` can evict and recreate pods with new requests.
- Q4: Why can `Recreate` mode cause application disruption?
  A: Evicting pods removes running instances temporarily and can interrupt traffic.
- Q5: Why should you start with VPA recommendations before applying changes automatically?
  A: To review and validate recommendations to avoid unexpected evictions or unsuitable resource settings.

6) sessions/03-ingress/README.md
- Q1: Why do the frontend and API Services remain `ClusterIP`?
  A: They are internal endpoints; the Ingress exposes traffic externally and routes to ClusterIP Services.
- Q2: What does the Ingress controller create in AWS?
  A: An external Load Balancer (ELB/NLB) plus cloud-specific resources (target groups, security groups).
- Q3: Why is `/api/users` routed to a different Service from `/api/apps`?
  A: Ingress path rules map different URL paths to different backend Services.
- Q4: Why does the frontend call APIs by Kubernetes Service DNS inside the cluster?
  A: Service DNS provides stable, internal discovery and avoids external routing/NAT.
- Q5: How would a custom domain point to the Ingress load balancer?
  A: Create DNS A/CNAME records that resolve the custom domain to the load balancer's DNS/name or IP.

7) sessions/01-core-k8s/README.md (Core Review Questions)
- Q1: Why do we create a Namespace first?
  A: To isolate resources and scope the lab, making management and cleanup simpler.
- Q2: Why does Flask need a ConfigMap and Secret?
  A: ConfigMap for non-sensitive configuration; Secret for credentials and sensitive data.
- Q3: Why does PostgreSQL need a Service even though users do not access it directly?
  A: To provide a stable network name/IP so other Pods can reliably connect.
- Q4: What is the limitation of a standalone Pod?
  A: It lacks self-healing, scaling, and declarative updates; it won't be recreated on failure.
- Q5: What does a Deployment add on top of Pods?
  A: Replica management, rolling updates, and declarative desired state.
- Q6: How does a Service know which Pods should receive traffic?
  A: By matching Pod labels with the Service's label selector.

8) sessions/02-storage-pv-pvc-statefulset/README.md
- Q1: Why does PostgreSQL need persistent storage?
  A: To preserve database data across Pod restarts and node failures.
- Q2: What is the difference between a PV and a PVC?
  A: PV is a cluster storage resource; PVC is a request/claim by a Pod that binds to a PV.
- Q3: Why is `hostPath` useful for learning but risky for production?
  A: It's node-local and simple for demos but not portable, resilient, or secure for production.
- Q4: What does a StorageClass add?
  A: Dynamic provisioning parameters and a way to select storage backends and performance characteristics.
- Q5: Why does a StatefulSet fit PostgreSQL better than a normal Deployment?
  A: It provides stable network identities and stable persistent volume claims per replica.

9) sessions/05-production-scaling/subsessions/05-node-autoscaling/README.md
- Q1: Why do Pods become Pending?
  A: Because the scheduler cannot find nodes with required resources, labels, or tolerations, or quota blocks them.
- Q2: Why does HPA not solve Pending Pods by itself?
  A: HPA changes replica counts but does not provision node capacity; without nodes Pods remain Pending.
- Q3: What does Cluster Autoscaler change in AWS?
  A: It adjusts Auto Scaling Group sizes (adds/removes EC2 nodes) based on unschedulable Pods.
- Q4: What does Karpenter create when it provisions capacity?
  A: New cloud instances (nodes) and associated Kubernetes Node objects tailored to Pod requirements.
- Q5: Why does EKS Auto Mode need the `eks.amazonaws.com/compute-type: auto` selector in the sample?
  A: To allow Auto Mode to identify and manage workloads eligible for automatic compute provisioning.
- Q6: Why should scale-down be slower than scale-up?
  A: To avoid flapping and accidental deletion of capacity needed again shortly after scale-up.
- Q7: What cost risk appears if you forget to delete an inflate workload?
  A: Unnecessary provisioned nodes and running instances causing ongoing cloud cost.

10) sessions/05-production-scaling/README.md
- Q1: Why is HPA alone not enough when the cluster has no free node capacity?
  A: HPA can request more Pods but cannot add nodes; an autoscaler or manual capacity change is required.
- Q2: What happens when ResourceQuota blocks new Pods?
  A: Pod creation is rejected or stays Pending; the API returns quota-related errors/events.
- Q3: Why can a LimitRange help teams use HPA safely?
  A: It enforces sensible defaults/limits for requests and limits, preventing oversized pods from starving cluster resources.
- Q4: Why is memory HPA different from CPU HPA in behavior?
  A: Memory usage is not easily averaged down and can cause OOM; memory signals do not drop predictably like CPU.
- Q5: When should an app scale on custom metrics instead of CPU or memory?
  A: When business-level or application-specific metrics (queue length, requests/sec, latency) better reflect load.
- Q6: What kind of disruption does a PDB protect against?
  A: Too many simultaneous voluntary evictions or rolling updates that reduce available replicas below a threshold.
- Q7: What is the difference between Cluster Autoscaler and Karpenter?
  A: Cluster Autoscaler adjusts ASG sizes; Karpenter provisions flexible nodes quickly with more scheduling-aware decisions.
- Q8: What does EKS Auto Mode manage for you?
  A: Automated node provisioning, scaling, and management for eligible workloads in the cluster.
- Q9: What should you check when Pods are Pending?
  A: Node capacity, resource requests/limits, taints/tolerations, node selectors/affinity, events, and ResourceQuota.

11) sessions/05-production-scaling/subsessions/01-resource-guardrails/README.md
- Q1: What is the difference between LimitRange and ResourceQuota?
  A: LimitRange sets default/limits per Pod/container; ResourceQuota limits total resource consumption for a namespace.
- Q2: Why does HPA need resource requests?
  A: To calculate utilization percentages against a known requested amount.
- Q3: What happens when a Deployment tries to create Pods beyond quota?
  A: Pod creation is rejected or marked Pending; API returns quota errors and events are emitted.
- Q4: Why is a namespace-level quota useful in a shared cluster?
  A: It enforces fair resource sharing and prevents a single tenant from exhausting cluster capacity.

12) sessions/05-production-scaling/subsessions/03-custom-external-metrics-hpa/README.md
- Q1: Why might CPU be a poor scaling signal for a queue worker?
  A: Queue length or backlog, not CPU, may be the true indicator of work pending.
- Q2: What does a metrics adapter do?
  A: Exposes custom or external metrics to the Kubernetes metrics API so HPA can consume them.
- Q3: What is the difference between custom and external metrics?
  A: Custom metrics are tied to Kubernetes objects (pods/services); external metrics are global or external to k8s objects.
- Q4: Why must metric labels map cleanly to Kubernetes resources?
  A: So HPA can correlate metric values to the specific resources it should scale.
- Q5: Why does HPA choose the highest recommendation when multiple metrics are configured?
  A: To satisfy all constraints and ensure the most-demanding metric's requirement is met.

13) sessions/04-hpa-vpa/subsessions/02-hpa-cpu-autoscaling/README.md
(Answers reproduced from the lesson)
- Q1: Why does this Deployment need a CPU request?
  A: So HPA can calculate utilization and the scheduler can reserve capacity.
- Q2: What happens when the load generator starts?
  A: Pod CPU usage rises and HPA increases replicas as utilization exceeds the target.
- Q3: Why does HPA update the Deployment instead of creating Pods directly?
  A: HPA modifies the Deployment's `spec.replicas`; the Deployment manages Pod creation.
- Q4: What does `maxReplicas` protect against?
  A: Excessive or runaway scaling that could exhaust cluster capacity.
- Q5: Why does scale-down happen slower than scale-up?
  A: Stabilization windows and conservative downscaling policies avoid churn.

14) sessions/05-production-scaling/subsessions/02-memory-hpa/README.md
- Q1: Why does memory HPA need memory requests?
  A: To know the baseline amount to compare current memory usage against.
- Q2: Why can memory scale-down be slower than CPU scale-down?
  A: Memory usage tends not to decrease quickly and aggressive downscaling can trigger OOMs; conservative behavior avoids instability.
- Q3: When is memory a good scaling signal?
  A: For apps where memory grows with load (caches, in-memory buffers) and closely correlates to capacity needs.
- Q4: Why should you keep `maxReplicas` conservative?
  A: To limit cost and prevent runaway provisioning that exhausts cluster resources.

15) sessions/05-production-scaling/subsessions/04-pdb-and-vpa-safety/README.md
- Q1: What is a voluntary disruption?
  A: An administrative or controller-triggered eviction (rolling update, node drain, VPA eviction) that removes pods intentionally.
- Q2: Why does PDB matter with VPA `Recreate` mode?
  A: VPA evictions can reduce available replicas; PDB prevents evicting too many pods at once, protecting availability.
- Q3: Why does a single-replica app not get much protection from PDB?
  A: With one replica you cannot maintain both availability and updates; PDB cannot guarantee availability if only a single pod exists.
- Q4: Why is `minAvailable: 100%` dangerous during node maintenance?
  A: It blocks evictions and can prevent node drains or maintenance from proceeding.
- Q5: How does PDB interact with node autoscaler scale-down?
  A: PDB can prevent nodes from being removed if evicting those pods would violate the PDB.

---
File with answers: [REVIEW_ANSWERS.md](REVIEW_ANSWERS.md)
