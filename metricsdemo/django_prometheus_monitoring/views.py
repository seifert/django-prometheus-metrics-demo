from django.apps import apps
from django.http import HttpResponse
from django.views.generic import View


class MetricsView(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.monitoring = apps.get_app_config(
            "django_prometheus_monitoring"
        ).monitoring

    def get(self, *args, **kwargs):
        return HttpResponse(
            self.monitoring.get_stats(), content_type="text/plain"
        )
