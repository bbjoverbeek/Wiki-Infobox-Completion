import sys
import json
from typing import Literal
import requests
from tqdm import tqdm
from more_itertools import chunked
from pprint import pprint

# use user agent to prevent API from blocking requests
USER_AGENT = 'infobox_completion_bot/1.0 (b.b.j.overbeek@student.rug.nl)'

# set to True to get properties for each city instead of all properties
PER_CITY = True


def get_entity_properties(entity_id: str) -> set[str]:
    """Get all property ids from an entity (id)"""

    # make request to wikidata API
    url = f'https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json'
    params = {
        'User-Agent': USER_AGENT,
        'format': 'json',
        'max_retries': 10,
        'dely_between_retries': 2,
    }
    results_json = requests.get(url, params, timeout=10).json()

    # get all properties from the entity
    entity_properties = set(results_json['entities'][entity_id]['claims'])

    return entity_properties


def get_property_names(
    properties: dict[str, dict], lang: Literal['en', 'nl', 'both'] = 'both'
) -> dict[str, dict[Literal['en', 'nl'], str]]:
    """Retrieve the name of properties in dict in a given language. Adds the
    name in the language to the dict and returns the dict."""
    # convert both to proper format for request
    if lang == 'both':
        lang = 'en|nl'

    # make request per 50 properties (this is the limit)
    for properties_batch in tqdm(
        chunked(properties, 50),
        desc='Getting property names',
        total=len(properties) // 50,
        leave=False,
    ):
        # convert property_ids to string
        property_ids_str = '|'.join(properties_batch)

        # make request to wikidata API
        url = f'https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids={property_ids_str}&languages={lang}'
        params = {
            'format': 'json',
            'max_retries': 10,
            'dely_between_retries': 2,
        }
        results_json = requests.get(url, params, timeout=10).json()

        # add result to final dict
        for property_id, value in results_json['entities'].items():
            for lang in value['labels']:
                properties[property_id][lang] = value['labels'][lang]['value']

    return properties


def create_all_properties_dict(cities: list[dict[str, str]]) -> dict[str, dict]:
    """Create a dictionary with all properties, their translation, and their
    absolute and relative frequency.
    """

    # get a set of all occuring properties and add key to dict for each
    properties = dict()
    for city in tqdm(cities, desc='Getting properties', leave=False):
        city_property_ids = get_entity_properties(city['uri'].split('/')[-1])
        for property_id in city_property_ids:
            if properties.get(property_id, None) is None:
                properties[property_id] = {
                    'en': '',
                    'nl': '',
                    'absolute_frequency': 1,
                    'relative_frequency': 0,
                }
            else:
                properties[property_id]['absolute_frequency'] += 1

    # calculate relative frequency
    for property_id, value in properties.items():
        value['relative_frequency'] = value['absolute_frequency'] / len(cities)

    # get the Dutch and English name for each property
    properties = get_property_names(properties)

    return properties


def create_cities_properties_dict(
    cities: list[dict[str, str]], all_properties_path: str
) -> dict[str, dict]:
    """Create a dictionary with all cities, their properties, and the
    translation of these properties. Uses the all_properties json to limit
    requests to the server.
    """

    city_properties = dict()

    with open(all_properties_path, 'r', encoding='utf-8') as inp:
        all_properties = json.load(inp)

    for city in tqdm(cities, desc='Getting properties per city', leave=False):
        city_properties[city['name']] = dict()
        city_property_ids = get_entity_properties(city['uri'].split('/')[-1])
        for property_id in city_property_ids:
            city_properties[city['name']][property_id] = dict()
            city_properties[city['name']][property_id]['nl'] = all_properties[
                property_id
            ].get('nl', '')
            city_properties[city['name']][property_id]['en'] = all_properties[
                property_id
            ].get('en', '')

    return city_properties


def main(argv: list[str]):
    """Retrieves all properties from a list of cities and their wikidata URI's
    Run with: python get_properties.py ./data/cities.json ./data/all_properties.json
    To get properties per city, set PER_CITY to True and run again.
    """
    # open file with cities and their wikidata URI's
    with open(argv[1], 'r', encoding='utf-8') as inp:
        cities = json.load(inp)

    if PER_CITY:
        # create properties dict with properties per city
        properties = create_cities_properties_dict(cities, './data/all_properties.json')

    else:
        # create properties dictionary with all properties and their frequency
        properties = create_all_properties_dict(cities)

    # pprint(properties)

    # write properties to file
    with open(argv[2], 'w', encoding='utf-8') as out:
        json.dump(properties, out, indent=4)

    if PER_CITY:
        print(
            f'Done, properties for {len(cities)} cities written to file: {argv[2]}',
            file=sys.stderr,
        )
    else:
        print(
            f'Done, {len(properties)} properties written to file: {argv[2]}',
            file=sys.stderr,
        )


if __name__ == '__main__':
    main(sys.argv)
