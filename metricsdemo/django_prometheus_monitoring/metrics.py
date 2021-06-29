import abc
import copy

import prometheus_client

from django.apps import apps


class BaseMetric(metaclass=abc.ABCMeta):
    def __init__(self, name, documentation, labelnames=None):
        self.name = name
        self.documentation = documentation
        self.labelnames = () if labelnames is None else labelnames

        self._labelvalues = None
        self._labelkwargs = None

        monitoring = apps.get_app_config(
            "django_prometheus_monitoring"
        ).monitoring
        if name in monitoring.metrics:
            raise ValueError(f"Metric {name} has been already registered")
        monitoring.metrics[name] = self
        self._monitoring = monitoring
        self._prometheus_inst = None

    def labels(self, *labelvalues, **labelkwargs):
        if not self.labelnames:
            raise ValueError("Label names has not been defined")
        if labelvalues and labelkwargs:
            raise ValueError(
                "Either labelvalues or labelkwargs may be passed, not both"
            )
        if labelvalues:
            if len(labelvalues) != len(self.labelnames):
                raise ValueError("Not enough labelvalues")
        else:
            if len(labelkwargs) != len(self.labelnames):
                raise ValueError("Not enough labelkwargs")

        new_inst = copy.copy(self)
        new_inst._labelvalues = labelvalues
        new_inst._labelkwargs = labelkwargs

        return new_inst

    @abc.abstractmethod
    def get_prometheus_inst(self):
        raise NotImplementedError


class Counter(BaseMetric):
    def get_prometheus_inst(self, registry=prometheus_client.REGISTRY):
        if self._prometheus_inst is None:
            self._prometheus_inst = prometheus_client.Counter(
                self.name,
                self.documentation,
                self.labelnames,
                registry=registry,
            )
        return self._prometheus_inst

    def inc(self, value=1):
        self._monitoring.counter_inc(
            self, value, *self._labelvalues, **self._labelkwargs
        )


class Summary(BaseMetric):
    def get_prometheus_inst(self, registry=prometheus_client.REGISTRY):
        if self._prometheus_inst is None:
            self._prometheus_inst = prometheus_client.Summary(
                self.name,
                self.documentation,
                self.labelnames,
                registry=registry,
            )
        return self._prometheus_inst

    def observe(self, value):
        self._monitoring.summary_observe(
            self, value, *self._labelvalues, **self._labelkwargs
        )


request_status = Counter(
    "request_status", "Request status", ["path", "method", "status"]
)

request_duration = Summary(
    "request_duration", "Request duration", ["path", "method"]
)
