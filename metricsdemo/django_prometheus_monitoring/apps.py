from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string

from .backends.dummy import DummyMonitoring


class MetricsConfig(AppConfig):
    name = "metricsdemo.django_prometheus_monitoring"
    monitoring = None

    def ready(self):
        monitoring_setting = getattr(settings, "MONITORING", {})
        backend_name = monitoring_setting.get("BACKEND")
        if backend_name:
            backend_cls = import_string(backend_name)
            self.monitoring = backend_cls()
        else:
            self.monitoring = DummyMonitoring()
