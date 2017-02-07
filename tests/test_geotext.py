# -*- coding: utf-8 -*-
from collections import OrderedDict

import pytest

from geotext import GeoText
from geotext.resources import get_words_counts


@pytest.mark.parametrize(
    (
        'fuzzy,limit,skip_nationalities,text,'
        'cities,countries,nationalities,country_mentions'
    ),
    [
        (
            False, 0, False, 'London is a great city', ['London', ], [], [],
            OrderedDict([(u'GB', 1,), ]),
        ),
        (
            False, 0, False, 'Voronezh and New York',
            ['Voronezh', 'New York', ], [], [],
            OrderedDict([(u'RU', 1,), (u'US', 1,), ]),
        ),
        (
            False, 0, False,
            "I am from Washington. So I'm American, although I live in "
            "Manchester.",
            ['Washington', 'Manchester', ], [], ['American', ],
            OrderedDict([(u'GB', 2,), (u'US', 1,), ]),
        ),
        (
            False, 0, True,
            "I am from Washington. So I'm American, although I live in "
            "Manchester.",
            ['Washington', 'Manchester', ], [], [],
            OrderedDict([(u'GB', 2,), ]),
        ),
        (
            False, 0, False, 'IT consultant from Germany', [], ['Germany', ],
            [], OrderedDict([(u'DE', 1,), ]),
        ),
        (False, 0, False, 'germany london', [], [], [], OrderedDict(),),
        (
            True, 0, False, 'germany london', ['London', ], ['Germany', ], [],
            OrderedDict([(u'DE', 1,), (u'GB', 1,), ]),
        ),
        (
            True, 0, False,
            'name of the munich writer, singer and photographer',
            ['Munich', 'Of', ], [], [],
            OrderedDict([(u'DE', 1,), (u'TR', 1,), ]),
        ),
        (
            True, 500000, False,
            'name of the munich writer, singer and photographer',
            ['Munich', ], [], [], OrderedDict([(u'DE', 1,), ]),
        ),
        (
            True, 0, False, 'Voronezh and NY', ['Voronezh', 'New York', ], [],
            [], OrderedDict([(u'RU', 1,), (u'US', 1,), ]),
        ),
        (
            False, 0, False, 'I live in Washington DC', ['Washington, D.C.', ],
            [], [], OrderedDict([(u'US', 1,), ]),
        ),
        (
            False, 0, False, 'I live in Washington D.C.', [], [], [],
            OrderedDict(),
        ),
        (
            True, 0, False, 'I live in Washington D.C. but used to live in NY',
            ['Washington, D.C.', 'New York', ], [], [],
            OrderedDict([(u'US', 2,), ]),
        ),
        (
            True, 0, False, 'I am from Izumiōtsu but lived in Воронеж',
            ['Izumiotsu', 'Voronezh', ], [], [],
            OrderedDict([(u'RU', 1,), (u'JP', 1,), ]),
        ),
    ]
)
def test_read(
    fuzzy, limit, skip_nationalities, text, cities, countries, nationalities,
    country_mentions
):
    geo_text = GeoText().set_population_limit(limit)
    geo_text.read(text, fuzzy=fuzzy, skip_nationalities=skip_nationalities)
    assert set(geo_text.cities) == set(cities)
    assert set(geo_text.countries) == set(countries)
    assert set(geo_text.nationalities) == set(nationalities)
    assert geo_text.country_mentions == country_mentions


@pytest.mark.parametrize(
    'phrases,result',
    [
        ([], set(),),
        (['hello', 'hi', ], {1, },),
        (['hello', 'hi', 'hello, world and all', ], {1, 4, },),
    ]
)
def test_get_words_counts(phrases, result):
    assert get_words_counts(phrases) == result
