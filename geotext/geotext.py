# -*- coding: utf-8 -*-

import re
from collections import namedtuple, Counter, OrderedDict

from tasks.db_tasks import (
    create_country_db, create_state_db, create_city_db, create_nationality_db,
    create_city_abbreviations_db, create_country_abbreviations_db,
)
from text_utils import get_words_counts, replace_non_ascii


class GeoText(object):
    """
    Extract cities and countries from a text

    Examples
    --------

    >>> geo_text = GeoText()
    >>> geo_text.read('London is a great city')
    >>> geo_text.cities
    ["London"]

    >>> GeoText().read('New York, Texas, and also China').country_mentions
    OrderedDict([(u'US', 2), (u'CN', 1)])
    """
    LOCATION_REGEX = r"[A-Z]+[a-z]*(?:[ '-][A-Z]+[a-z]*)*"
    GeoDB = namedtuple(
        'GeoDB',
        'country_db,state_db,city_db,nationality_db,city_abbreviation_db,'
        'country_abbreviation_db'
    )
    Results = namedtuple('Results', 'countries,states,cities')

    def __init__(self, text=''):
        self.results = GeoText.Results((), (), ())
        self.text = text
        self._build_geodb()
        if text:
            self.read(text)

    def _build_geodb(self):
        """
        Load information from the data directory

        :type min_population: int, process only cities having this
            population min

        Returns
        -------
        A namedtuple with three fields: nationalities cities countries
        """
        country_db = create_country_db()
        state_db = create_state_db(country_db)
        city_db = create_city_db(state_db, country_db)
        nationality_db = create_nationality_db(country_db)
        city_abbreviation_db = create_city_abbreviations_db(city_db)
        country_abbreviation_db = create_country_abbreviations_db(country_db)
        self._geodb = GeoText.GeoDB(
            country_db, state_db, city_db, nationality_db,
            city_abbreviation_db, country_abbreviation_db
        )
        self._location_length = self._get_locations_length()

    def _get_locations_length(self):
        words_counts = set()
        for collection in self._geodb:
            words_counts |= get_words_counts(
                [place._search_field for place in collection.all()]
            )
        return sorted(words_counts, reverse=True)

    def _get_candidates(self, text, fuzzy):
        """
        :param text
        :param fuzzy  if set to True analyze all words in the text regardless
            of capitalization
        """
        text = replace_non_ascii(text)
        if not fuzzy:
            text = re.sub(r'[^\x00-\x7F]+', ' ', text).strip()
            return map(
                lambda x: x.lower(), re.findall(GeoText.LOCATION_REGEX, text)
            )
        # Remove dots from acronyms:
        text = re.sub(r'\.(?![a-z]{2})', '', text, flags=re.IGNORECASE)
        # Replace other symbols with spaces
        # TODO: improve this, since DB has unicode symbols in cities
        text = re.sub(r'[^\w]+', ' ', text).strip()

        candidates = set()
        for location_length in self._location_length:
            text_substring = text
            while text_substring:
                candidates |= set(re.findall(
                    r"\w+(?:[ '-]\w+){{{}}}".format(location_length - 1),
                    text_substring
                ))
                text_substring = ' '.join(text_substring.split()[1:])
        return list(candidates) + map(lambda x: x.lower(), candidates)

    def read(
        self, text, min_population=0, skip_nationalities=False, fuzzy=True
    ):
        self.text = text
        candidates = self._get_candidates(text, fuzzy=fuzzy)
        (
            countries, states, cities,
        ) = self._get_locations_from_candidates(
            candidates, min_population, skip_nationalities
        )
        self.results = GeoText.Results(countries, states, cities)
        return self

    def get_country_mentions(self):
        states_to_ignore = set()
        countries_to_ignore = set()
        country_mentions = []
        for city in self.results.cities:
            country_mentions.append(city.country)
            if city.state:
                states_to_ignore.add(city.state)
            countries_to_ignore.add(city.country)
        for state in self.results.states:
            if state in states_to_ignore:
                continue
            country_mentions.append(state.country)
            countries_to_ignore.add(state.country)
        for country in self.results.countries:
            if country in countries_to_ignore:
                continue
            country_mentions.append(country)
        return OrderedDict(
            Counter(country_mentions).most_common()
        )

    def _get_locations_from_candidates(
        self, candidates, min_population, skip_nationalities
    ):
        countries, states, cities = set(), set(), set()
        cities_by_search_fields = dict()
        for candidate in candidates:
            # When iterating over the candidates we apply the following
            # priorities:
            # 1) Cities abbreviations: NYC or LA (since e.g. LA usually
            #    means Los Angeles, not Louisiana)
            # 2) US short states names: "CA" (California)
            # 3) Countries + country codes: "GB", "RU"
            # 4) Nationalities (treated as countries found)
            # 5) Countries abbreviations: other shortcuts, like "USA" or "UK"
            # 6) Cities
            # 7) Full text state names: "Texas"

            # 1
            city_abbrev_match = self._geodb.city_abbreviation_db.search(
                candidate
            )
            if (
                city_abbrev_match and
                city_abbrev_match.place.population >= min_population
            ):
                    cities.add(city_abbrev_match.place)
                    continue

            # 2
            state_match = (
                self._geodb.state_db.search('US.{}'.format(candidate))
            )
            if (
                state_match and
                state_match.country.population >= min_population
            ):
                states.add(state_match)
                continue

            # 3
            country_match = self._geodb.country_db.search(candidate)
            if country_match and country_match.population >= min_population:
                countries.add(country_match)
                continue

            # 4
            if not skip_nationalities:
                nationality_match = self._geodb.nationality_db.search(
                    candidate
                )
                if (
                    nationality_match and
                    nationality_match.place.population >= min_population
                ):
                    countries.add(nationality_match.place)
                    continue

            # 5
            country_abbrev_match = self._geodb.country_abbreviation_db.search(
                candidate
            )
            if (
                country_abbrev_match and
                country_abbrev_match.place.population >= min_population
            ):
                countries.add(country_abbrev_match.place)
                continue

            # 6
            # City names may overlap and be present inside other cities, e.g.
            # there's San Francisco in US and San in Mali and if the text is
            # "I am from San Francisco", both of these cities will be found.
            # We need to remove all cities detected that are substings of other
            # found cities

            def is_substring(substring, text):
                return bool(re.findall(r'\b{}\b'.format(substring), text))
            city_match = self._geodb.city_db.search(candidate)
            if city_match and city_match.population >= min_population:
                for other_city in cities_by_search_fields.keys():
                    if city_match._search_field == other_city:
                        # Skip same city detected
                        break
                    if is_substring(city_match._search_field, other_city):
                        # Do not add this city to results
                        break
                    if is_substring(other_city, city_match._search_field):
                        # Remove city that's a substring of current one
                        cities.remove(cities_by_search_fields.pop(other_city))
                else:
                    cities.add(city_match)
                    cities_by_search_fields[
                        city_match._search_field
                    ] = city_match
                continue

            # 7
            state_match = (
                self._geodb.state_db.search(candidate)
            )
            if (
                state_match and
                state_match.country.population >= min_population
            ):
                states.add(state_match)
                continue
        return tuple(countries), tuple(states), tuple(cities)
