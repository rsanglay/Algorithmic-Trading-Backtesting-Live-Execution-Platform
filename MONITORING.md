# Monitoring & Observability

The backend now exposes Prometheus-compatible metrics and structured logging to help you operate the platform.

## Metrics endpoint

- Route: `GET /metrics`
- Format: Prometheus text
- Exposed metrics:
  - `trading_platform_http_requests_total` – request counter labelled by method, path, status
  - `trading_platform_http_request_duration_seconds` – request latency histogram

### Scraping locally
```
curl http://localhost:8001/metrics
```

Integrate this endpoint with Prometheus/Grafana by configuring a scrape job pointing to the backend service.

## Logging

Existing middleware already emits structured logs with request IDs. Combine logs with metrics for better alerting and debugging.

## Future ideas
- Push metrics to a remote Prometheus/InfluxDB instance
- Add alert rules for latency, error rate, and cache hit ratio
