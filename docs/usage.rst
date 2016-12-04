========
Usage
========

To use geotext in a project::

    from geotext import GeoText

    geo_text = GeoText()
    geo_text.read('London is a great city')
    geo_text.cities
    # "London"

    GeoText().read('Voronezh and New York').country_mentions
    # OrderedDict([(u'RU', 1), (u'US', 1)])
