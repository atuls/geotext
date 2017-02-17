# -*- coding: utf-8 -*-
from geotext.models.place import Place


class State(Place):
    def __init__(self, key, name, search_field, country):
        super(State, self).__init__(key, name, search_field)
        self.country = country

    def __repr__(self):
        return '{}: {}, {}'.format(
            type(self).__name__, self.name, self.country.name
        )
