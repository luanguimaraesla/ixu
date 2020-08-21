from collections import defaultdict


class Metric():
    '''
    Openmetrics representation of any metric
    '''

    def __init__(self, kind, name, description):
        self.kind = kind
        self.name = name
        self.description = description
        self.metrics = dict()

    def __str__(self):
        return f"{self.help_header}\n{self.type_header}\n{self.metrics_content}"

    @property
    def help_header(self):
        return f"# HELP {self.name} {self.description}"

    @property
    def type_header(self):
        return f"# TYPE {self.name} {self.kind}"

    @property
    def metrics_content(self):
        content = ""

        for tags, value in self.metrics.items():
            tags_list = [f'{k}="{v}"' for k, v in tags]
            tags_text = "{" + ",".join(tags_list) + "}" if len(tags_list) else ""
            content += f"{self.name}{tags_text} {value}\n"

        return content.strip()

    def make_tags_ref(self, tags):
        '''
        Converts a dict to an unmutable reference
        to be used as a key
        '''

        return tuple(tags.items())


class Counter(Metric):
    '''
    Openmetrics representation of counters
    '''

    def __init__(self, name, description):
        super().__init__("counter", name, description)

        self.metrics = defaultdict(int)

    def inc(self, num=1, tags={}):
        '''
        Increments the counter
        '''

        self.metrics[self.make_tags_ref(tags)] += num

class Gauge(Metric):
    '''
    Openmetrics representation of gauges
    '''

    def __init__(self, name, description):
        super().__init__("gauge", name, description)

        self.metrics = defaultdict(float)

    def add(self, num, tags=()):
        '''
        Add a value to a gauge
        '''

        self.metrics[self.make_tags_ref(tags)] += num


class Exporter():
    '''
    Exporter class is used to build simple openmetrics file
    without importing any complex lib such as prometheus-client
    '''

    def __init__(self):
        self._counters = dict()
        self._gauges = dict()

    def counter(self, name, description=""):
        '''
        Returns a counter reference if it's already registered or
        create a new one if it's missing
        '''

        if name in self._counters:
            return self._counters[name]

        self._counters[name] = Counter(name, description)
        return self._counters[name]

    def gauge(self, name, description=""):
        '''
        Returns a gauge reference if it's already registered or
        create a new one if it's missing
        '''

        if name in self._gauges:
            return self._gauges[name]

        self._gauges[name] = Gauge(name, description)
        return self._gauges[name]

    def __str__(self):
        content = ""

        for counter in self._counters.values():
            content += f"{counter}\n"

        for gauge in self._gauges.values():
            content += f"{gauge}\n"

        return content

