from . import Monitoring


class DummyMonitoring(Monitoring):
    def get_stats(self):
        return "# dummy metrics"

    def counter_inc(self, metric, value, *labelvalues, **labelkwargs):
        pass

    def summary_observe(self, metric, value, *labelvalues, **labelkwargs):
        pass
