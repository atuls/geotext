# -*- coding: utf-8 -*-

import re
from collections import namedtuple, Counter, OrderedDict

from resources import (
    get_nationalities_data, get_countries_data, get_cities_data,
    get_words_counts,
)


class GeoText(object):
    """
    Extract cities and countries from a text

    Examples
    --------

    >>> geo_text = GeoText()
    >>> geo_text.read('London is a great city')
    >>> geo_text.cities
    "London"

    >>> GeoText().read('New York, Texas, and also China').country_mentions
    OrderedDict([(u'US', 2), (u'CN', 1)])
    """
    LOCATION_REGEX = r"[A-Z]+[a-z]*(?:[ '-][A-Z]+[a-z]*)*"
    Index = namedtuple('Index', 'nationalities cities countries')

    def __init__(self):
        self.countries = []
        self.cities = []
        self.nationalities = []
        self.country_mentions = OrderedDict()
        self._build_index()

    def _update_code_to_country(self):
        self.code_to_country = dict(
            zip(self._index.countries.values(), self._index.countries.keys())
        )

    def set_population_limit(self, min_population):
        """
        :type min_population: int, process only cities having this
            population min
        """
        self._build_index(min_population)
        return self

    def _build_index(self, min_population=0):
        """
        Load information from the data directory

        :type min_population: int, process only cities having this
            population min

        Returns
        -------
        A namedtuple with three fields: nationalities cities countries
        """
        self._index = GeoText.Index(
            get_nationalities_data(),
            get_cities_data(min_population=min_population),
            get_countries_data()
        )
        self._update_code_to_country()
        self._location_length = self._get_locations_length()

    def _get_locations_length(self):
        words_counts = set()
        for collection in self._index:
            words_counts |= get_words_counts(collection)
        return sorted(words_counts, reverse=True)

    def get_candidates(self, text, fuzzy=False):
        """
        :param text
        :param fuzzy  if set to True analyze all words in the text regardless
            of capitalization
        """
        def capitalize_list(l):
            return map(lambda w: w.title(), l)

        text = ' '.join(re.sub(r'[^\w]+', ' ', text).split())
        if not fuzzy:
            return capitalize_list(re.findall(GeoText.LOCATION_REGEX, text))
        candidates = set()
        for location_length in self._location_length:
            text_substring = text
            while text_substring:
                candidates |= set(re.findall(
                    r"\w+(?:[ '-]\w+){{{}}}".format(location_length - 1),
                    text_substring
                ))
                text_substring = ' '.join(text_substring.split()[1:])
        return capitalize_list(candidates)

    def read(self, text, fuzzy=False):
        candidates = self.get_candidates(text, fuzzy=fuzzy)
        self.countries = [
            each for each in candidates
            if each.lower() in self._index.countries
        ]
        cities = [
            each for each in candidates
            if each.lower() in self._index.cities
            and each.lower() not in self._index.countries
        ]
        # Iterate over a copy because we'll modify this list
        for city in cities[:]:
            # Check whether it's a substring of other cities
            other_cities = cities[:]
            other_cities.remove(city)
            for other_city in other_cities:
                if re.findall(r'\b{}\b'.format(city), other_city):
                    cities.remove(city)
                    break
        self.cities = cities
        self.nationalities = [
            each for each in candidates
            if each.lower() in self._index.nationalities
        ]

        # Calculate number of country mentions
        country_mentions = [
            self._index.countries[country.lower()]
            for country in self.countries
        ]
        country_mentions.extend(
            [self._index.cities[city.lower()] for city in self.cities]
        )
        country_mentions.extend(
            [
                self._index.nationalities[nationality.lower()]
                for nationality in self.nationalities
            ]
        )
        self.country_mentions = OrderedDict(
            Counter(country_mentions).most_common()
        )
        return self
