# -*- coding: utf-8 -*-

import re
from collections import namedtuple, Counter, OrderedDict

from resources import (
    get_nationalities_data, get_countries_data, get_cities_data,
)


class GeoText(object):
    """
    Extract cities and countries from a text

    Examples
    --------

    >>> geo_text = GeoText()
    >>> places = geo_text.read('London is a great city')
    >>> places.cities
    "London"

    >>> GeoText().read('New York, Texas, and also China').country_mentions
    OrderedDict([(u'US', 2), (u'CN', 1)])
    """
    LOCATION_REGEX = r"[A-Z]+[a-z]*(?:[ '-][A-Z]+[a-z]*)*"

    def __init__(self, min_population=0):
        """
        :type min_population: int, process only cities having this
            population min
        """
        self.countries = []
        self.cities = []
        self.nationalities = []
        self.country_mentions = OrderedDict()
        self.index = GeoText.build_index(min_population)

    @staticmethod
    def build_index(min_population=0):
        """
        Load information from the data directory

        :type min_population: int, process only cities having this
            population min

        Returns
        -------
        A namedtuple with three fields: nationalities cities countries
        """
        Index = namedtuple('Index', 'nationalities cities countries')
        return Index(
            get_nationalities_data(),
            get_cities_data(min_population=min_population),
            get_countries_data()
        )

    def read(self, text):
        candidates = re.findall(GeoText.LOCATION_REGEX, text)
        self.countries = [
            each for each in candidates if each.lower() in self.index.countries
        ]
        self.cities = [
            each for each in candidates
            if each.lower() in self.index.cities
            and each.lower() not in self.index.countries
        ]
        self.nationalities = [
            each for each in candidates
            if each.lower() in self.index.nationalities
        ]

        # Calculate number of country mentions
        country_mentions = [
            self.index.countries[country.lower()]
            for country in self.countries
        ]
        country_mentions.extend(
            [self.index.cities[city.lower()] for city in self.cities]
        )
        country_mentions.extend(
            [
                self.index.nationalities[nationality.lower()]
                for nationality in self.nationalities
            ]
        )
        self.country_mentions = OrderedDict(
            Counter(country_mentions).most_common()
        )
        return self
