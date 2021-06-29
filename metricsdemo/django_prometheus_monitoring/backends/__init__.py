import abc


class Monitoring(abc.ABC):
    def __init__(self):
        self.metrics = {}

    @abc.abstractmethod
    def get_stats(self):
        raise NotImplementedError

    @abc.abstractmethod
    def counter_inc(self, metric, value, *labelvalues, **labelkwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def summary_observe(self, metric, value, *labelvalues, **labelkwargs):
        raise NotImplementedError
