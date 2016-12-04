# -*- coding: utf-8 -*-
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data_path(path):
    return os.path.join(_ROOT, 'data', path)


COUNTRIES_FILE = get_data_path('countryInfo.txt')
CITIES_FILE = get_data_path('cities15000.txt')
CITIES_PATCH_FILE = get_data_path('citypatches.txt')
NATIONALITIES_FILE = get_data_path('nationalities.txt')


def _read_data_file(
    filename, usecols=(0, 1), sep='\t', comment='#', encoding='utf-8',
    population_field_num=None, filter_method=None
):
    """
    Parse data files from the data directory

    Data files are provided by GeoNames service: http://www.geonames.org/
    Files format defined in GeoNames readme file:
    http://download.geonames.org/export/dump/readme.txt

    Parameters
    ----------
    filename: string
        Full path to file

    usecols: list, default [0, 1]
        A list of two elements representing the columns to be parsed into a
        dictionary.
        The first element will be used as keys and the second as values.
        Defaults to the first two columns of `filename`.

    sep : string, default '\t'
        Field delimiter.

    comment : str, default '#'
        Indicates remainder of line should not be parsed. If found at the
        beginning of a line, the line will be ignored altogether. This
        parameter must be a single character.

    encoding : string, default 'utf-8'
        Encoding to use for UTF when reading/writing (ex. `utf-8`)

    population_field_num : int, default None
        If set: this should define the field with location population count to
        use for conflicts resolution: if there're several locations with same
        name, the one with larger population will be taken.
        If set to None, only the last one will be taken.

    filter_method: method, default None
        Only lines that pass this filter are used
        Method receives one param: line split by defined separator into a list

    Returns
    -------
    A dictionary with the same length as the number of lines in `filename`
    """

    with open(filename, 'rb') as f:
        # filter comment lines
        lines = (line for line in f if not line.startswith(comment))

        d = dict()
        location_population = dict()
        for line in lines:
            columns = line.split(sep)
            if filter_method and not filter_method(columns):
                continue
            key = columns[usecols[0]].decode(encoding).lower()
            # 'London City' -> 'London'
            suffix_to_remove = ' city'
            if key.endswith(suffix_to_remove):
                key = key[:-len(suffix_to_remove)]

            value = columns[usecols[1]].decode(encoding).rstrip('\n')
            if population_field_num is not None:
                population = int(
                    columns[population_field_num].decode(encoding)
                )
                if key in d and location_population[key] > population:
                    continue
                location_population[key] = population
            d[key] = value
    return d


def get_nationalities_data():
    return _read_data_file(NATIONALITIES_FILE, sep=':')


def get_countries_data():
    return _read_data_file(COUNTRIES_FILE, usecols=[4, 0])


def get_cities_data(min_population=0):
    # Field 14 is population, see
    # http://download.geonames.org/export/dump/readme.txt
    # for reference
    cities = _read_data_file(
        CITIES_FILE, usecols=[1, 8],
        population_field_num=14,
        filter_method=lambda fields: int(fields[14]) > min_population
    )
    return cities


def get_words_counts(phrases_list):
    """
    Set of phrases lengths
    e.g.
    get_words_count(['hello', 'hi']) -> {1,}
    get_words_count(['hello', 'hi', 'hello, world and all']) -> {1, 3}
    """
    return set(map(len, map(lambda phrase: phrase.split(), phrases_list)))
