# Sub-Session 04: VPA Recommendations

This sub-session demonstrates Vertical Pod Autoscaler.

The lab creates:

- A `vpa-demo` Deployment.
- A `vpa-demo` ClusterIP Service.
- A `vpa-demo` VerticalPodAutoscaler in `Off` mode.
- A `vpa-load-generator` Deployment that continuously sends requests.

## How The Demo Works

The Deployment uses the same CPU-burning example image as the HPA lab:

```text
registry.k8s.io/hpa-example
```

This image is intentionally separate from the message-board images because the VPA lab needs a standalone CPU-load target without PostgreSQL dependencies.

The initial CPU request is intentionally small:

```yaml
cpu: 25m
memory: 64Mi
```

VPA watches usage and writes recommendations into:

```text
.status.recommendation
```

In `Off` mode, VPA does not change the running Pods. It only recommends.

## Apply The Workload

From `sessions/04-hpa-vpa`:

```bash
kubectl apply -f subsessions/01-prerequisites-and-namespace/
kubectl apply -f subsessions/04-vpa-recommendations/01-vpa-demo-deployment.yml
```

Check:

```bash
kubectl get deployment vpa-demo -n tb-app-autoscaling
kubectl get pods -n tb-app-autoscaling -l app=vpa-demo
kubectl get service vpa-demo -n tb-app-autoscaling
```

## Apply VPA In Recommendation Mode

```bash
kubectl apply -f subsessions/04-vpa-recommendations/02-vpa-recommendation-only.yml
```

Check:

```bash
kubectl get vpa -n tb-app-autoscaling
kubectl describe vpa vpa-demo -n tb-app-autoscaling
```

At first, recommendations may be empty. VPA needs metrics over time.

## Start Load

```bash
kubectl apply -f subsessions/04-vpa-recommendations/04-vpa-load-generator.yml
```

Watch metrics:

```bash
kubectl top pods -n tb-app-autoscaling
```

Check recommendations:

```bash
kubectl describe vpa vpa-demo -n tb-app-autoscaling
```

Important recommendation fields:

- `Lower Bound`: minimum suggested request.
- `Target`: recommended request for normal operation.
- `Upper Bound`: higher safe request based on observed usage.
- `Uncapped Target`: recommendation before min/max policy limits are applied.

Recommendation:
    Container Recommendations:
      Container Name:  vpa-demo
      Lower Bound:
        Cpu:     25m
        Memory:  250Mi
      Target:
        Cpu:     25m
        Memory:  250Mi
      Uncapped Target:
        Cpu:     25m
        Memory:  250Mi
      Upper Bound:
        Cpu:     1
        Memory:  512Mi

These values mean:

- `Lower Bound` is the minimum safe request based on observed usage and the VPA policy.
- `Target` is the recommended request for normal operation.
- `Uncapped Target` is the recommendation before the VPA policy limits such as `minAllowed` or `maxAllowed` are enforced.
- `Upper Bound` is the maximum request VPA may recommend, often controlled by the VPA policy limits.

In this example, VPA is recommending:

- keep CPU at `25m` because the observed CPU usage does not need a larger CPU request yet,
- increase memory request to `250Mi` because the pod is using more memory than the original `64Mi` request,
- and allow up to `1` CPU and `512Mi` memory if the workload grows, but do not force that higher value now.

## Optional: Apply Recommendations With Recreate

Do this only after students understand that VPA may evict Pods.

```bash
kubectl apply -f subsessions/04-vpa-recommendations/03-vpa-auto-recreate.yml
```

Delete a Pod so the Deployment creates a replacement:

```bash
kubectl delete pod -n tb-app-autoscaling -l app=vpa-demo
kubectl get pods -n tb-app-autoscaling -w
```

Inspect the new Pod resources:

```bash
kubectl get pod -n tb-app-autoscaling -l app=vpa-demo -o jsonpath="{.items[0].spec.containers[0].resources}"
```

You should see requests influenced by the VPA recommendation.

## Stop Load

```bash
kubectl delete -f subsessions/04-vpa-recommendations/04-vpa-load-generator.yml --ignore-not-found
```

## Return VPA To Recommendation Mode

If you applied `Recreate` mode and want to return to safe mode:

```bash
kubectl apply -f subsessions/04-vpa-recommendations/02-vpa-recommendation-only.yml
```

## Cleanup

```bash
kubectl delete -f subsessions/04-vpa-recommendations/ --ignore-not-found
```

## Review Questions

1. Why does VPA need Metrics Server?
2. What does VPA write into its status?
3. What is the difference between `Off` and `Recreate` mode?
4. Why can `Recreate` mode cause application disruption?
5. Why should you start with VPA recommendations before applying changes automatically?

## Review Answers

1. VPA needs Metrics Server because it relies on live container resource usage data to generate recommendations. Without metrics, VPA cannot see how much CPU or memory the pod is actually using.
2. VPA writes its recommendations into `.status.recommendation` on the VerticalPodAutoscaler object. This includes `Lower Bound`, `Target`, `Uncapped Target`, and `Upper Bound` for each container.
3. `Off` mode means VPA only recommends resources and does not change running pods. `Recreate` mode means VPA can evict pods and recreate them with updated resource requests based on the recommendation.
4. `Recreate` mode can cause disruption because evicting pods temporarily removes application instances. During recreation, traffic may be interrupted or capacity may drop until new pods are ready.
5. Start with VPA recommendations first so you can review the suggested request changes before applying them. This avoids unexpected pod evictions and gives you control over whether the recommended values are appropriate for the application.
