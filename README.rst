===============================
geotext
===============================

Geotext extracts country and city mentions from text

* Free software: MIT license
* Documentation: https://geotext.readthedocs.org.

Usage
-----
.. code-block:: python

        from geotext import GeoText

        geo_text = GeoText()
        geo_text.read('London is a great city')
        geo_text.cities
        # "London"

        GeoText().read('New York, Texas, and also China').country_mentions
        # OrderedDict([(u'US', 2), (u'CN', 1)])

        GeoText().read('Voronezh and New York').country_mentions
        # OrderedDict([(u'RU', 1), (u'US', 1)])

        # Take only large cities into account
        GeoText().set_population_limit(1000000).read('Voronezh and New York').country_mentions
        # OrderedDict([(u'US', 1)])

Features
--------
- No external dependencies
- Fast
- Data from http://www.geonames.org licensed under the Creative Commons Attribution 3.0 License.

Similar projects
----------------
`geography
<https://github.com/ushahidi/geograpy>`_: geography is more advanced and bigger in scope compared to geotext and can do everything geotext does. On the other hand geotext is leaner: has no external dependencies, is faster (re vs nltk) and also depends on libraries and data covered with more permissive licenses.
