# Sub-Session 02: HPA CPU Autoscaling

This sub-session demonstrates Horizontal Pod Autoscaler using CPU utilization.

The lab creates:

- A `cpu-demo` Deployment.
- A `cpu-demo` ClusterIP Service.
- A `cpu-demo` HPA.
- A `load-generator` Deployment that continuously sends requests.

## How The Demo Works

The `cpu-demo` container uses the official Kubernetes HPA example image:

```text
registry.k8s.io/hpa-example
```

The app burns CPU when it receives HTTP requests. This image is intentionally separate from the message-board images because the HPA lab needs a lightweight CPU-load target without PostgreSQL dependencies.

The Deployment requests:

```yaml
cpu: 100m
memory: 64Mi
```

The HPA target is:

```text
50% average CPU utilization
```

So if the average Pod usage rises above about `50m` CPU, HPA starts increasing replicas.

## Apply The Workload

From `sessions/04-hpa-vpa`:

```bash
kubectl apply -f subsessions/01-prerequisites-and-namespace/
kubectl apply -f subsessions/02-hpa-cpu-autoscaling/01-cpu-demo-deployment.yml
```

Check:

```bash
kubectl get deployment cpu-demo -n tb-app-autoscaling
kubectl get pods -n tb-app-autoscaling -l app=cpu-demo
kubectl get service cpu-demo -n tb-app-autoscaling
kubectl top pods -n tb-app-autoscaling
```

## Apply The HPA

```bash
kubectl apply -f subsessions/02-hpa-cpu-autoscaling/02-cpu-demo-hpa.yml
```

Check:

```bash
kubectl get hpa cpu-demo -n tb-app-autoscaling
kubectl describe hpa cpu-demo -n tb-app-autoscaling
```

At first, replicas may stay at `1` because there is no load.

## Start Load

```bash
kubectl apply -f subsessions/02-hpa-cpu-autoscaling/03-load-generator.yml
```

Watch:

```bash
kubectl get hpa -n tb-app-autoscaling -w
```

In another terminal:

```bash
kubectl get deployment cpu-demo -n tb-app-autoscaling -w
```

Expected behavior:

- CPU utilization rises.
- HPA increases desired replicas.
- The Deployment creates more Pods.
- The Service load balances requests across the Pods.

## Inspect The Scaling Decision

```bash
kubectl describe hpa cpu-demo -n tb-app-autoscaling
```

Important fields:

- `Metrics`: current CPU compared to target CPU.
- `Min replicas`: lowest allowed replica count.
- `Max replicas`: highest allowed replica count.
- `Conditions`: whether HPA can get metrics and scale.
- `Events`: recent scale decisions.

## Stop Load

```bash
kubectl delete -f subsessions/02-hpa-cpu-autoscaling/03-load-generator.yml --ignore-not-found
```

HPA does not always scale down immediately. The manifest includes a scale-down stabilization window so students can observe that Kubernetes avoids fast up/down flapping.

Watch scale down:

```bash
kubectl get hpa -n tb-app-autoscaling -w
```

## Manual Reset

If you want to reset quickly:

```bash
kubectl delete hpa cpu-demo -n tb-app-autoscaling
kubectl scale deployment cpu-demo -n tb-app-autoscaling --replicas=1
kubectl apply -f subsessions/02-hpa-cpu-autoscaling/02-cpu-demo-hpa.yml
```

## Cleanup

```bash
kubectl delete -f subsessions/02-hpa-cpu-autoscaling/ --ignore-not-found
```

## Review Questions

1. Why does this Deployment need a CPU request?
2. What happens when the load generator starts?
3. Why does HPA update the Deployment instead of creating Pods directly?
4. What does `maxReplicas` protect against?
5. Why does scale-down happen slower than scale-up?

## Review Answers

1. The Deployment needs a CPU request so HPA can measure utilization relative to a known requested amount and so the scheduler can reserve capacity for the Pod. Without a CPU request, HPA cannot calculate percent utilization reliably.
2. When the load generator starts, it sends continuous HTTP traffic to `cpu-demo`, causing the app Pods to consume more CPU. As average CPU utilization rises above the HPA target, the HPA increases the Deployment replica count.
3. HPA updates the Deployment because the Deployment is the controller responsible for creating and managing Pods. HPA changes the Deployment's desired replica count, and the Deployment then creates or removes Pods to match that target.
4. `maxReplicas` protects against uncontrolled or excessive scaling by capping the number of Pods the HPA can create. This prevents the workload from consuming too much cluster capacity or creating more replicas than the application or infrastructure can handle.
5. Scale-down is slower than scale-up because the manifest includes a stabilization window and conservative scale-down policy to avoid pod churn. Kubernetes waits longer before removing Pods so temporary drops in load do not cause repeated scale-down and scale-up cycles.
