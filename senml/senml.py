# -*- coding: utf-8 -*-
"""@package senml.senml
SenML Python object representation

@todo Add CBOR support
"""

import attr


@attr.s
class SenMLMeasurement(object):
    """SenML data representation"""
    name = attr.ib(default=None)
    time = attr.ib(default=None)
    isotime = attr.ib(default=None)
    unit = attr.ib(default=None)
    value = attr.ib(default=None)
    sum = attr.ib(default=None)

    def to_absolute(self, base):
        """Convert values to include the base information

        Be aware that it is not possible to compute time average of the signal
        without the base object since the base time and base value are still
        needed for that use case."""
        attrs = {
            'name': (base.name or '') + (self.name or ''),
            'time': (base.time or 0.0) + (self.time or 0.0),
            'unit': self.unit or base.unit,
            'sum': self.sum,
            'isotime': self.isotime or base.isotime,
        }
        if isinstance(self.value, (bool, str, unicode)):
            attrs['value'] = self.value
        elif self.value is not None:
            attrs['value'] = (base.value or 0.0) + (self.value or 0.0)

        ret = self.__class__(**attrs)
        return ret

    @classmethod
    def base_from_json(cls, data):
        """Create a base instance from the given SenML data"""
        template = cls()
        attrs = {
            'name': data.get('bn', template.name),
            'time': data.get('bt', template.time),
            'isotime': data.get('biso8601', template.isotime),
            'unit': data.get('bu', template.unit),
            'value': data.get('bv', template.value),
        }
        return cls(**attrs)

    @classmethod
    def from_json(cls, data):
        """Create an instance given JSON data as a dict"""
        template = cls()
        attrs = {
            'name': data.get('n', template.name),
            'time': data.get('t', template.time),
            'isotime': data.get('iso8601', template.isotime),
            'unit': data.get('u', template.unit),
            'value': data.get('v', template.value),
            'sum': data.get('s', template.sum),
        }
        if attrs['value'] is None:
            if 'vs' in data:
                attrs['value'] = unicode(data['vs'])
            elif 'vb' in data:
                attrs['value'] = bool(data['vb'])
            elif 'vd' in data:
                attrs['value'] = str(data['vd'])

        return cls(**attrs)

    def to_json(self):
        """Format the entry as a SenML+JSON object"""
        ret = {}
        if self.name is not None:
            ret['n'] = unicode(self.name)

        if self.time is not None:
            ret['t'] = float(self.time)

        if self.isotime is not None:
            ret['iso8601'] = unicode(self.isotime)

        if self.unit is not None:
            ret['u'] = unicode(self.unit)

        if self.sum is not None:
            ret['s'] = float(self.sum)

        if isinstance(self.value, bool):
            ret['vb'] = self.value
        elif isinstance(self.value, str):
            ret['vd'] = self.value
        elif isinstance(self.value, unicode):
            ret['vs'] = self.value
        elif self.value is not None:
            ret['v'] = float(self.value)

        return ret




class SenMLDocument(object):
    """A collection of SenMLMeasurement data points"""

    measurement_factory = SenMLMeasurement

    def __init__(self, measurements=None, base=None, *args, **kwargs):
        """
        Constructor
        """

        super(SenMLDocument, self).__init__(*args, **kwargs)
        self.measurements = measurements
        self.base = base

    @classmethod
    def from_json(cls, json_data):
        """Parse a loaded SenML JSON representation into a SenMLDocument

        @param[in] json_data  JSON list, from json.loads(senmltext)
        """
        # Grab base information from first entry
        base = cls.measurement_factory.base_from_json(json_data[0])

        measurements = [cls.measurement_factory.from_json(item) for item in json_data]

        obj = cls(base=base, measurements=measurements)

        return obj

    def to_json(self):
        """Return a JSON dict"""
        first = {
            # Add SenML version
            'bver': 5,
        }
        if self.base:
            base = self.base

            if base.name is not None:
                first['bn'] = unicode(base.name)
            if base.time is not None:
                first['bt'] = float(base.time)
            if base.unit is not None:
                first['bu'] = unicode(base.unit)
            if base.value is not None:
                first['bv'] = float(base.value)
            if base.isotime is not None:
                first['bisotime'] = unicode(base.isotime)

        if self.measurements:
            first.update(self.measurements[0].to_json())
            ret = [first]
            ret.extend([item.to_json() for item in self.measurements[1:]])
        else:
            ret = []

        return ret

    def to_normalized_json(self):
        """
        Return a JSON dict
        """
        return [item.to_absolute(self.base).to_json() for item in self.measurements]
