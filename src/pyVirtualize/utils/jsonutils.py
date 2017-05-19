
import json
import urlparse
from datetime import datetime


class DateTimeDecoder(json.JSONDecoder):

    def __init__(self, date_format, *args, **kwargs):
        self.date_format = date_format
        json.JSONDecoder.__init__(self, object_hook=self.date_to_object, *args, **kwargs)

    def date_to_object(self, d):
        for k, v in d.items():
            if not (isinstance(d[k], str) or isinstance(d[k], unicode)):
                continue
            try:
                d[k] = datetime.strptime(d[k], self.date_format)
            except:
                pass
        return d


class URLDecoder(json.JSONDecoder):

    def __init__(self, base_url, key_contains=[], *args, **kwargs):
        self.base_url = base_url
        self.key_contains = key_contains
        json.JSONDecoder.__init__(self, object_hook=self.url_to_object, *args, **kwargs)

    def url_to_object(self, d):
        for k, v in d.items():
            if not (isinstance(d[k], str) or isinstance(d[k], unicode)):
                continue
            if any([True for i in self.key_contains if k.__contains__(i)]) is True:
                d[k] = urlparse.urljoin(self.base_url, d[k])
        return d


class DateTimeEncoder(json.JSONEncoder):

    def __init__(self, date_format, *args, **kwargs):
        self.date_format = date_format
        super(DateTimeEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(self.date_format)
        else:
            return json.JSONEncoder.default(self, obj)
