__author__ = 'rramchandani'

import os
import argparse

import yaml
import yaml.constructor

from os.path import sep
from collections import OrderedDict, defaultdict


def get_file_extension(file_path):
    filename = os.path.basename(file_path)
    extension = filename.split(".")[-1]
    return extension


def parse_dict(_):

    if isinstance(_, list):
        for count in range(0, len(_)):
            _[count] = parse_dict(_[count])
    elif isinstance(_, dict):
        for k, v in _.items():
            _[k] = parse_dict(v)
    elif isinstance(_, str) or isinstance(_, unicode):
        try:
            _ = int(_)
        except:
            try:
                _ = float(_)
            except:
                try:
                    _ = basestring(_)
                except:
                    pass
    return _


def normalize_keys_of_dict(dict_):
    _ = OrderedDict()
    for k, v in dict_.items():
        if isinstance(v, list) or isinstance(v, tuple):
            li = []
            for item in v:
                if isinstance(item, dict) or isinstance(item, OrderedDict) or isinstance(item, defaultdict):
                    li.append(normalize_keys_of_dict(item))
                else:
                    li.append(item)
            _[k.lower()] = li
        elif isinstance(v, dict) or isinstance(v, OrderedDict) or isinstance(v, defaultdict):
            _[k.lower()] = normalize_keys_of_dict(v)
        else:
            _[k.lower()] = v

    return _


def xmlparse(input_file, parse_values=True, normalize_keys=True, **kwargs):

    import xmltodict
    with open(input_file) as fh:
        _ = xmltodict.parse(xml_input=fh, **kwargs)

    if normalize_keys:
        _ = normalize_keys_of_dict(_)

    return parse_dict(_) if parse_values else _


def iniparse(input_file, parse_values=True, normalize_keys=True, **kwargs):

    import ConfigParser

    cp = ConfigParser.ConfigParser()
    cp.read(input_file)

    _ = OrderedDict()
    for section in cp.sections():
        sec = section.lower() if normalize_keys else section
        _[sec] = OrderedDict()
        for items in cp.items(section):
            i = items[0].lower() if normalize_keys else items[0]
            _[sec][i] = items[1]

    return parse_dict(_) if parse_values else _


class GenericParsers(object):

    def __init__(self, file_path, parse_values=True, normalize_keys=True):
        self._file_path = file_path
        self._parse_values = parse_values
        self._normalize_keys = normalize_keys
        self._current_parser = None
        extension = get_file_extension(self._file_path)
        if extension == "xml":
            self._current_parser = xmlparse
        elif extension == "ini":
            self._current_parser = iniparse

    def parse(self):
        if self._current_parser is None:
            raise NotImplemented("Cannot parse {0} file.".format(os.path.basename(self._file_path)))

        parsed_object = self._current_parser(self._file_path, self._parse_values, self._normalize_keys)

        return parsed_object


class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


if __name__ == '__main__':
    x = GenericParsers(file_path=r"C:\PythonProjects\flexbats\config\variables.ini")
    _ = x.parse()
    import pprint
    pprint.pprint(_)
