import logging
import threading
import time

import ipcqueue.posixmq
import prometheus_client.registry

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import BaseCommand

from ...backends.prometheus import PrometheusMultiprocessMonitoring

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process Prometheus metrics"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        monitoring = apps.get_app_config(
            "django_prometheus_monitoring"
        ).monitoring

        if not isinstance(monitoring, PrometheusMultiprocessMonitoring):
            raise ImproperlyConfigured(
                "Monitoring backend is not instance of "
                "PrometheusMultiprocessMonitoring"
            )

        self.monitoring = monitoring
        self.metrics_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.registry = prometheus_client.registry.CollectorRegistry(
            auto_describe=True
        )

    def handle(self, *args, **options):
        metrics_collector = threading.Thread(target=self.count_stats)
        metrics_collector.start()
        try:
            self.consume_metrics()
        finally:
            self.stop_event.set()

    def consume_metrics(self):
        while 1:
            try:
                (
                    metric_cls,
                    name,
                    documentation,
                    labelnames,
                    method,
                    value,
                    labelvalues,
                    labelkwargs,
                ) = self.monitoring.queue.get(block=True)

                if name not in self.monitoring.metrics:
                    metric = metric_cls(name, documentation, labelnames)
                else:
                    metric = self.monitoring.metrics[name]
                prometheus_metric = metric.get_prometheus_inst(self.registry)

                self.metrics_lock.acquire()
                try:
                    if labelvalues or labelkwargs:
                        prometheus_metric = prometheus_metric.labels(
                            *labelvalues, **labelkwargs
                        )
                    getattr(prometheus_metric, method)(value)
                finally:
                    self.metrics_lock.release()
            except ipcqueue.posixmq.QueueError as exc:
                logger.error("Queue error: %d %s", exc.errno, exc.msg)
            except Exception as exc:
                logger.exception("Metrics consumer error: %s", exc)

    def count_stats(self):
        while 1:
            try:
                self.metrics_lock.acquire()
                try:
                    stats = prometheus_client.generate_latest(self.registry)
                finally:
                    self.metrics_lock.release()
                self.monitoring.set_stats(stats)
                wait_for_event(self.stop_event, 5.0)
            except Exception as exc:
                logger.exception("Metrics collector error: %s", exc)


def wait_for_event(event, seconds, step=0.1):
    for unused in range(int(seconds / step)):
        if event.is_set():
            return
        time.sleep(0.1)


def run_metrics_consumer():
    call_command(__name__.split(".")[-1])
