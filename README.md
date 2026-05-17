# Assignment 6: Automation in SRE, Capacity Planning and Load Testing

This package contains a complete mini e-commerce API and SRE automation setup:

- `analysis/traffic_forecast.py` - extracts server logs and forecasts 6-month traffic growth.
- `data/access.log` - sample server access log.
- `app/app.py` - FastAPI e-commerce API.
- `Dockerfile` - container image for the API.
- `k8s/deployment.yaml` - Kubernetes Deployment with CPU requests/limits.
- `k8s/service.yaml` - Kubernetes Service.
- `k8s/hpa.yaml` - Horizontal Pod Autoscaler with 80% CPU threshold.
- `load_test/locustfile.py` - Locust traffic spike simulation.
- `run_commands_mac.md` - exact commands for Mac + VS Code.
- `report/Assignment_6_Report.docx` and `.pdf` - report draft.

Important: the report has placeholders for Kubernetes and Locust screenshots. Run the commands and insert your own screenshots before final submission.
