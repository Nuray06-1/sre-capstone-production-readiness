import argparse
import os
import re
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) [^"]+" (?P<status>\d+) (?P<size>\d+) (?P<response_ms>\d+)'
)


def parse_access_log(log_path: Path) -> pd.DataFrame:
    rows = []
    with log_path.open("r", encoding="utf-8") as file:
        for line in file:
            match = LOG_PATTERN.search(line)
            if not match:
                continue
            data = match.groupdict()
            timestamp = datetime.strptime(data["ts"], "%d/%b/%Y:%H:%M:%S %z")
            rows.append({
                "timestamp": timestamp,
                "month": timestamp.strftime("%Y-%m"),
                "method": data["method"],
                "path": data["path"],
                "status": int(data["status"]),
                "response_ms": int(data["response_ms"]),
            })
    return pd.DataFrame(rows)


def try_read_elasticsearch(index_name: str) -> pd.DataFrame | None:
    """Optional ELK integration. If ELASTICSEARCH_URL is not set, script uses local access.log."""
    elastic_url = os.getenv("ELASTICSEARCH_URL")
    if not elastic_url:
        return None
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(elastic_url)
        response = es.search(index=index_name, size=10000, query={"match_all": {}})
        rows = []
        for hit in response["hits"]["hits"]:
            src = hit["_source"]
            ts = pd.to_datetime(src.get("timestamp") or src.get("@timestamp"), utc=True)
            rows.append({
                "timestamp": ts,
                "month": ts.strftime("%Y-%m"),
                "path": src.get("path", "/"),
                "status": int(src.get("status", 200)),
                "response_ms": int(src.get("response_ms", 0)),
            })
        return pd.DataFrame(rows)
    except Exception as exc:
        print(f"ELK connection failed, using local log file instead: {exc}")
        return None


def build_forecast(monthly: pd.Series, months_ahead: int = 6) -> tuple[pd.DataFrame, float]:
    monthly = monthly.sort_index()
    growth = monthly.pct_change().dropna()
    avg_growth = growth.mean()

    last_month = pd.Period(monthly.index[-1], freq="M")
    last_value = float(monthly.iloc[-1])

    forecast_rows = []
    for step in range(1, months_ahead + 1):
        future_month = (last_month + step).strftime("%Y-%m")
        predicted = round(last_value * ((1 + avg_growth) ** step))
        forecast_rows.append({"month": future_month, "forecast_requests": int(predicted)})

    return pd.DataFrame(forecast_rows), avg_growth


def save_chart(monthly: pd.Series, forecast: pd.DataFrame, output_path: Path, avg_growth: float):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(monthly.index, monthly.values, marker="o", label="Historical traffic")
    plt.plot(forecast["month"], forecast["forecast_requests"], marker="o", linestyle="--", label="6-month forecast")
    plt.title(f"Traffic Forecast | Average Monthly Growth: {avg_growth * 100:.2f}%")
    plt.xlabel("Month")
    plt.ylabel("Requests")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)


def main():
    parser = argparse.ArgumentParser(description="Extract API logs and forecast traffic growth for SRE capacity planning.")
    parser.add_argument("--log", default="data/access.log", help="Path to local access.log")
    parser.add_argument("--index", default="server-logs", help="Elasticsearch index name if ELASTICSEARCH_URL is configured")
    parser.add_argument("--csv-output", default="outputs/monthly_traffic_forecast.csv")
    parser.add_argument("--chart-output", default="outputs/traffic_forecast.png")
    args = parser.parse_args()

    df = try_read_elasticsearch(args.index)
    if df is None or df.empty:
        df = parse_access_log(Path(args.log))

    if df.empty:
        raise SystemExit("No valid log records found.")

    monthly = df.groupby("month").size()
    forecast, avg_growth = build_forecast(monthly, months_ahead=6)

    monthly_df = monthly.rename("actual_requests").reset_index()
    result = pd.merge(monthly_df, forecast, on="month", how="outer")
    Path(args.csv_output).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.csv_output, index=False)
    save_chart(monthly, forecast, Path(args.chart_output), avg_growth)

    print("Monthly traffic:")
    print(monthly_df.to_string(index=False))
    print(f"\nAverage monthly traffic growth: {avg_growth * 100:.2f}%")
    print("\nForecast for next 6 months:")
    print(forecast.to_string(index=False))
    print(f"\nSaved CSV: {args.csv_output}")
    print(f"Saved chart: {args.chart_output}")


if __name__ == "__main__":
    main()
