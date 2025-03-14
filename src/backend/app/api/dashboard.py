from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import prometheus_client
from prometheus_client import start_http_server
import json

router = APIRouter()

# Prometheus metrics
REQUEST_COUNT = prometheus_client.Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'route', 'status']
)

REQUEST_LATENCY = prometheus_client.Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['route']
)

ERROR_COUNT = prometheus_client.Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['route']
)

CPU_USAGE = prometheus_client.Gauge(
    'container_cpu_usage_seconds_total',
    'Container CPU usage in seconds',
    ['container']
)

# Mock data for development
MOCK_METRICS = {
    'requestRate': [
        {'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(), 'value': 100 + i * 10}
        for i in range(30)
    ],
    'responseTime': [
        {'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(), 'value': 50 + i * 5}
        for i in range(30)
    ],
    'errorRate': [
        {'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(), 'value': 2 + i * 0.5}
        for i in range(30)
    ],
    'cpuUsage': [
        {'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(), 'value': 30 + i * 2}
        for i in range(30)
    ]
}

MOCK_ALERTS = [
    {
        'id': '1',
        'severity': 'warning',
        'title': 'High CPU Usage',
        'description': 'CPU usage is above 80% for the last 5 minutes',
        'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat()
    },
    {
        'id': '2',
        'severity': 'critical',
        'title': 'Deployment Failed',
        'description': 'Production deployment failed',
        'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat()
    }
]

MOCK_DEPLOYMENTS = [
    {
        'environment': 'production',
        'status': 'success',
        'lastDeployed': (datetime.now() - timedelta(hours=1)).isoformat(),
        'version': '1.0.0'
    },
    {
        'environment': 'staging',
        'status': 'in_progress',
        'lastDeployed': (datetime.now() - timedelta(minutes=5)).isoformat(),
        'version': '1.0.1'
    },
    {
        'environment': 'development',
        'status': 'failed',
        'lastDeployed': (datetime.now() - timedelta(hours=2)).isoformat(),
        'version': '1.0.2'
    }
]

@router.get("/metrics")
async def get_metrics() -> Dict[str, List[Dict[str, Any]]]:
    """Get system metrics data."""
    try:
        # In production, this would fetch real metrics from Prometheus
        return MOCK_METRICS
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts() -> List[Dict[str, Any]]:
    """Get active alerts."""
    try:
        # In production, this would fetch alerts from Alertmanager
        return MOCK_ALERTS
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deployments")
async def get_deployments() -> List[Dict[str, Any]]:
    """Get deployment status for all environments."""
    try:
        # In production, this would fetch deployment status from Kubernetes
        return MOCK_DEPLOYMENTS
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/record")
async def record_metrics(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Record new metrics data."""
    try:
        # In production, this would record metrics to Prometheus
        REQUEST_COUNT.labels(
            method=metrics.get('method', 'unknown'),
            route=metrics.get('route', 'unknown'),
            status=metrics.get('status', 'unknown')
        ).inc()

        REQUEST_LATENCY.labels(
            route=metrics.get('route', 'unknown')
        ).observe(metrics.get('duration', 0))

        if metrics.get('status', '').startswith('5'):
            ERROR_COUNT.labels(
                route=metrics.get('route', 'unknown')
            ).inc()

        CPU_USAGE.labels(
            container=metrics.get('container', 'unknown')
        ).set(metrics.get('cpu_usage', 0))

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start Prometheus metrics server
start_http_server(8000) 