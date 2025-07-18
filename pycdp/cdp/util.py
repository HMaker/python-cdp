import typing


T_JSON_DICT = typing.Dict[str, typing.Any]
_event_parsers = dict()


class UnknownObject:
    def __init__(self, elements: dict):
        self._elements = elements

    def __getattr__(self, name):
        # some names are appended a `_` so they don't collide with the python namespace
        # example: id_ and type_
        name = name.removesuffix('_')

        if name not in self._elements:
            raise AttributeError

        return self._elements[name]

    @classmethod
    def from_json(cls, json: T_JSON_DICT):
        if isinstance(json, dict):
            value = {key: cls.from_json(val) for key, val in json.items()}
            obj = cls(value)
        elif isinstance(json, list):
            obj = [cls.from_json(val) for val in json]
        else:
            obj = json

        return obj


class UnknownEvent(UnknownObject):
    def __init__(self, name, elements):
        super().__init__(elements)
        self.name = name

    @classmethod
    def from_json(cls, json: T_JSON_DICT):
        name = json['method']
        obj = UnknownObject.from_json(json['params'])

        if isinstance(obj, UnknownObject):
            return cls(name, obj._elements)

        return obj


def event_class(method):
    ''' A decorator that registers a class as an event class. '''
    def decorate(cls):
        _event_parsers[method] = cls
        return cls
    return decorate


def parse_json_event(json: T_JSON_DICT) -> typing.Any:
    ''' Parse a JSON dictionary into a CDP event. '''
    if json['method'] not in _event_parsers:
        return UnknownEvent.from_json(json)

    return _event_parsers[json['method']].from_json(json['params'])
