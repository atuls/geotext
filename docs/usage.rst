========
Usage
========

To use geotext in a project::

    from geotext import GeoText

    geo_text = GeoText()
    geo_text.read(
        "I'm French, but live in NY. "
        "I like to visit my friends in France from time to time."
    )
    geo_text.cities
    # ['New York']
    geo_text.countries
    # ['France']
    geo_text.nationalities
    # ['French']
    geo_text.country_mentions
    # OrderedDict([('FR', 2), ('US', 1)])

    GeoText().read('Voronezh and NY').country_mentions
    # OrderedDict([(u'RU', 1), (u'US', 1)])
