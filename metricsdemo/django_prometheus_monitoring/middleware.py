import time

from .metrics import request_duration, request_status


class RequestMonitoringMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        request_duration.labels(
            path=request.path,
            method=request.method,
        ).observe(duration)
        request_status.labels(
            path=request.path,
            method=request.method,
            status=response.status_code,
        ).inc(1)

        return response
