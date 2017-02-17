# -*- coding: utf-8 -*-
from geotext.models.place import Place


class City(Place):
    def __init__(self, key, name, search_field, population, state, country):
        super(City, self).__init__(key, name, search_field, population)
        self.state = state
        self.country = country

    def __repr__(self):
        return '{}: {}, {}, {}'.format(
            type(self).__name__, self.name,
            self.state.name if self.state else '', self.country.name
        )
