import fcntl
import logging
import queue
import os

import ipcqueue.posixmq

from django.conf import settings

from . import Monitoring

logger = logging.getLogger(__name__)


class PrometheusMultiprocessMonitoring(Monitoring):
    def __init__(self):
        super().__init__()
        monitoring_setting = getattr(settings, "MONITORING", {})
        self.queue = ipcqueue.posixmq.Queue(
            name=monitoring_setting["QUEUE_NAME"],
            maxsize=monitoring_setting.get("QUEUE_MAX_SIZE", 10),
            maxmsgsize=monitoring_setting.get("QUEUE_MAX_MSG_SIZE", 1024),
        )
        self.result_file = monitoring_setting["RESULT_FILE"]

    def get_stats(self):
        data = b""
        fd = os.open(
            self.result_file,
            os.O_CREAT | os.O_RDONLY,
            mode=0o644,
        )
        try:
            fcntl.flock(fd, fcntl.LOCK_SH)
            try:
                while 1:
                    part = os.read(fd, 4096)
                    if not part:
                        break
                    data += part
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
        return data

    def set_stats(self, stats):
            fd = os.open(
                self.result_file,
                os.O_CREAT | os.O_WRONLY,
                mode=0o644,
            )
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
                try:
                    os.ftruncate(fd, 0)
                    os.write(fd, stats)
                finally:
                    fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    def counter_inc(self, metric, value, *labelvalues, **labelkwargs):
        try:
            self.queue.put(
                (
                    metric.__class__,
                    metric.name,
                    metric.documentation,
                    metric.labelnames,
                    "inc",
                    value,
                    labelvalues,
                    labelkwargs,
                ),
                block=True,
                timeout=0.1,
            )
        except queue.Full:
            logger.warning("Queue is full")
        except ipcqueue.posixmq.QueueError as exc:
            logger.error("Queue error: %d %s", exc.errno, exc.msg)
        except Exception as exc:
            logger.exception("Increment %s error: %s", metric.name, exc)

    def summary_observe(self, metric, value, *labelvalues, **labelkwargs):
        try:
            self.queue.put(
                (
                    metric.__class__,
                    metric.name,
                    metric.documentation,
                    metric.labelnames,
                    "observe",
                    value,
                    labelvalues,
                    labelkwargs,
                ),
                block=True,
                timeout=0.1,
            )
        except queue.Full:
            logger.warning("Queue is full")
        except ipcqueue.posixmq.QueueError as exc:
            logger.error("Queue error: %d %s", exc.errno, exc.msg)
        except Exception as exc:
            logger.exception("Observe %s error: %s", metric.name, exc)
