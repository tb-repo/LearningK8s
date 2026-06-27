# Session 01: Core Kubernetes Objects

This session implements the standalone Flask/PostgreSQL app in Kubernetes one step at a time.

App source:

```text
../../three-tier-flask-postgres-app
```

App image used by this session:

```text
prashantdey/appk8stutorial:1.0
```

Storage is intentionally simple in this session. PostgreSQL uses `emptyDir`, so database data can disappear when the database Pod is replaced. Persistent storage is handled in Session 02.

## Sub-Session Order

Follow the sub-sessions in this order:

1. `subsessions/01-namespace`: isolate the app resources in a namespace.
2. `subsessions/02-configmap-secret`: provide app configuration and credentials.
3. `subsessions/03-postgres-deployment-service`: run PostgreSQL and give it a stable internal DNS name.
4. `subsessions/04-flask-pod`: run the app as a single Pod to understand Pod basics.
5. `subsessions/05-flask-deployment`: replace the standalone Pod with a Deployment.
6. `subsessions/06-flask-services`: expose the Flask Deployment using Services.

## Target Shape By The End

```text
Browser
  -> Flask Service
    -> Flask Deployment
      -> Flask Pods
        -> PostgreSQL Service
          -> PostgreSQL Deployment
            -> PostgreSQL Pod with ephemeral storage
```

## Build And Push App Image

From the app folder:

```bash
cd ../../three-tier-flask-postgres-app
docker build -t prashantdey/appk8stutorial:1.0 .
docker push prashantdey/appk8stutorial:1.0
```

Return to this session folder before applying manifests:

```bash
cd ../sessions/01-core-k8s
```

## Full Apply Order

From `sessions/01-core-k8s`:

```bash
kubectl apply -f subsessions/01-namespace/
kubectl apply -f subsessions/02-configmap-secret/
kubectl apply -f subsessions/03-postgres-deployment-service/
kubectl apply -f subsessions/05-flask-deployment/
kubectl apply -f subsessions/06-flask-services/
```

Use the standalone Pod sub-session before the Deployment sub-session when teaching Pod fundamentals.

## Full Cleanup

From `sessions/01-core-k8s`:

```bash
kubectl delete -f subsessions/06-flask-services/ --ignore-not-found
kubectl delete -f subsessions/05-flask-deployment/ --ignore-not-found
kubectl delete -f subsessions/04-flask-pod/ --ignore-not-found
kubectl delete -f subsessions/03-postgres-deployment-service/ --ignore-not-found
kubectl delete -f subsessions/02-configmap-secret/ --ignore-not-found
kubectl delete -f subsessions/01-namespace/ --ignore-not-found
```

## Core Review Questions

1. Why do we create a Namespace first?
2. Why does Flask need a ConfigMap and Secret?
3. Why does PostgreSQL need a Service even though users do not access it directly?
4. What is the limitation of a standalone Pod?
5. What does a Deployment add on top of Pods?
6. How does a Service know which Pods should receive traffic?


 
## Review Answers

1. To isolate resources for the lab scope and make cleanup/management easier.
2. ConfigMap for non-sensitive config; Secret for credentials and sensitive values.
3. A Service gives PostgreSQL a stable network name/IP so other Pods can connect reliably.
4. A standalone Pod has no self-healing, scaling, or rolling-update capabilities.
5. A Deployment adds replica management, rolling updates, and declarative desired state.
6. A Service matches Pod labels using its selector to decide which Pods receive traffic.

