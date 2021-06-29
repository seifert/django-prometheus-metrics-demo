from metricsdemo.settings import *

DEBUG = False

ALLOWED_HOSTS = ['*']

MONITORING = {
    "BACKEND": "metricsdemo.django_prometheus_monitoring.backends.prometheus.PrometheusMultiprocessMonitoring",
    "RESULT_FILE": "/tmp/metrics-demo-metrics",
    "QUEUE_NAME": "/metrics-demo",
    "QUEUE_MAX_SIZE": 10,
    "QUEUE_MAX_MSG_SIZE": 4096,
}
