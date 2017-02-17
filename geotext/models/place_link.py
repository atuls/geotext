# -*- coding: utf-8 -*-
from geotext.models.place import Place


class PlaceLink(Place):
    def __init__(self, key, name, search_field, place):
        super(PlaceLink, self).__init__(key, name, search_field)
        self.place = place
