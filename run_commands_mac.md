# Assignment 6 - Commands for Mac + VS Code

## 0. Open the project
```bash
cd sre_assignment6_package
```

## 1. Predictive analysis screenshot
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r analysis/requirements.txt
python analysis/traffic_forecast.py --log data/access.log
open outputs/traffic_forecast.png
```
Screenshot to take: terminal output + `outputs/traffic_forecast.png`.

## 2. Kubernetes + HPA
Start Docker Desktop first.

```bash
brew install minikube kubectl
minikube start --driver=docker
minikube addons enable metrics-server
```

Build image inside Minikube:
```bash
eval $(minikube docker-env)
docker build -t ecommerce-api:1.0 .
```

Deploy app and HPA:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl get pods
kubectl get hpa
```
Screenshot to take: `kubectl get hpa`.

## 3. Test API locally
```bash
kubectl port-forward svc/ecommerce-api-service 8080:80
```
Open another terminal:
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/products
```

## 4. Load testing with Locust
Open a new terminal:
```bash
source .venv/bin/activate
pip install -r load_test/requirements.txt
locust -f load_test/locustfile.py --host http://localhost:8080 --users 150 --spawn-rate 20 --run-time 3m --headless
```

While Locust is running, open another terminal:
```bash
kubectl get hpa -w
```

And another terminal:
```bash
kubectl get pods -w
```

Screenshots to take:
1. Locust terminal output.
2. `kubectl get hpa` showing increased CPU/load.
3. `kubectl get pods` showing more than 1 pod.

## 5. Clean up
```bash
kubectl delete -f k8s/hpa.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
minikube stop
```
