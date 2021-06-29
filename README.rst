Prometheus metrics in Django
============================

This demo explains how to use Prometheus metric in multiprocess environment.
Workers put metric into queue and separate process consumes messages from
queue and summarize metric from workers. Collected metrics are written into
file and workers serve content of this file. Uses ``ipcqueue.posixmq.Queue``,
so it works under Linux or other Posix systems. Probably does not work under
Windows (untested).

Usage
-----

settings.py
^^^^^^^^^^^

::

    INSTALLED_APPS = [
        ...,
        'metricsdemo.django_prometheus_monitoring.apps.MetricsConfig',
        ...,
    ]

    MIDDLEWARE = [
        'metricsdemo.django_prometheus_monitoring.middleware.RequestMonitoringMiddleware',  # Must be first
        ...,
    ]

    MONITORING = {
        "BACKEND": "metricsdemo.django_prometheus_monitoring.backends.prometheus.PrometheusMultiprocessMonitoring",
        "RESULT_FILE": "/tmp/metrics-demo-metrics",
        "QUEUE_NAME": "/metrics-demo",
        "QUEUE_MAX_SIZE": 10,
        "QUEUE_MAX_MSG_SIZE": 4096,
    }

For development purposes (for example, local development),
``metricsdemo.django_prometheus_monitoring.backends.dummy.DummyMonitoring``
backend can be used.

urls.py
^^^^^^^

::

    urlpatterns = [
        ...,
        path('metrics', MetricsView.as_view()),
        ...,
    ]

uwsgi.conf
^^^^^^^^^^

::

    [uwsgi]
    http=:8000
    master=1
    module=metricsdemo.wsgi
    processes=4
    mule=metricsdemo.django_prometheus_monitoring.management.commands.process_prometheus_metrics:run_metrics_consumer

Run server and try urls:

::

    $ uwsgi --ini conf/uwsgi.conf

    $ curl http://localhost:9000/
    $ curl http://localhost:9000/

    $ curl http://localhost:9000/metrics
    # HELP request_duration Request duration
    # TYPE request_duration summary
    request_duration_count{method="GET",path="/"} 2.0
    request_duration_sum{method="GET",path="/"} 0.018917083740234375
    # HELP request_duration_created Request duration
    # TYPE request_duration_created gauge
    request_duration_created{method="GET",path="/"} 1.6249951881070983e+09
    # HELP request_status_total Request status
    # TYPE request_status_total counter
    request_status_total{method="GET",path="/",status="200"} 2.0
    # HELP request_status_created Request status
    # TYPE request_status_created gauge
    request_status_created{method="GET",path="/",status="200"} 1.6249951881072655e+09

License
-------

3-clause BSD
