# Required Screenshots

1. Forecast output:
   - Terminal after `python analysis/traffic_forecast.py --log data/access.log`
   - Chart: `outputs/traffic_forecast.png`

2. HPA:
   - `kubectl get hpa`

3. Load test:
   - Locust headless output or Locust web UI
   - `kubectl get hpa` during load
   - `kubectl get pods` showing scaled replicas

Recommended screenshot names:
- screenshot_1_forecast_terminal.png
- screenshot_2_forecast_chart.png
- screenshot_3_hpa_initial.png
- screenshot_4_locust_load_test.png
- screenshot_5_hpa_scaled.png
- screenshot_6_pods_scaled.png
