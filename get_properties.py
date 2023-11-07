import sys
import json
import time
import requests
from tqdm import tqdm


from util import CityProperty, City, Property

# use user agent to prevent API from blocking requests
USER_AGENT = 'infobox_completion_bot/1.0 (b.b.j.overbeek@student.rug.nl)'





def get_entity_properties_and_labels(entity_id: str) -> dict[str, CityProperty]:
    """Get all property ids from an entity (id) using sparql"""

    url = 'https://query.wikidata.org/sparql'
    query = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        
        SELECT DISTINCT ?property ?propertyLabel_en ?propertyLabel_nl WHERE {{
          wd:{entity_id} ?p ?statement .
          ?property wikibase:directClaim ?p .
          
          OPTIONAL {{
            ?property rdfs:label ?propertyLabel_en .
            FILTER (lang(?propertyLabel_en) = "en")
          }}
          OPTIONAL {{
            ?property rdfs:label ?propertyLabel_nl .
            FILTER (lang(?propertyLabel_nl) = "nl")
          }}
        }}
    """

    headers = {
        'Accept': 'application/sparql-results+json,*/*;q=0.9',
        'User-Agent': 'python-requests/2.24.0',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {'query': query, 'format': 'json'}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        time.sleep(5)
        return get_entity_properties_and_labels(entity_id)

    return {
        item['property']['value']: CityProperty(
            id=item['property']['value'],
            label_en=item.get('propertyLabel_en', None)["value"] if item.get(
                'propertyLabel_en', None
            ) else None,
            label_nl=item.get('propertyLabel_nl', None)["value"] if item.get(
                'propertyLabel_nl', None)
            else None,
        )
        for item in response.json()['results']['bindings']
    }


def get_properties_per_city(cities: list[City]) -> dict[str, dict[str, CityProperty]]:
    """Get all properties for each city"""

    properties_per_city = dict()
    for city in tqdm(cities, desc='Getting properties per city'):
        entity_id = city.uri.split('/')[-1]
        properties_per_city[entity_id] = get_entity_properties_and_labels(entity_id)

    return properties_per_city


def create_all_properties_dict(
        properties_per_city: dict[str, dict[str, CityProperty]]
) -> dict[str, Property]:
    """Create a dictionary with all properties, their translation, and their
    absolute and relative frequency.
    """

    # get a set of all occuring properties and add key to dict for each
    all_properties = dict()
    for city, properties in tqdm(
            properties_per_city.items(), desc='Getting properties', leave=False
    ):
        for property_id, value in properties.items():
            if all_properties.get(property_id, None) is None:
                all_properties[property_id] = Property(
                    id=property_id,
                    label_en=value.label_en,
                    label_nl=value.label_nl,
                    absolute_frequency=1,
                    relative_frequency=0
                )
            else:
                all_properties[property_id].absolute_frequency += 1

    # calculate relative frequency
    for property_id, value in all_properties.items():
        all_properties[property_id].relative_frequency = \
            value.absolute_frequency / len(properties_per_city)

    return all_properties


def main(argv: list[str]):
    """Retrieves all properties from a list of cities and their wikidata URI's
    Run with: python get_properties.py ./data/cities.json ./data/all_properties.json
    To get properties per city, set PER_CITY to True and run again.
    """
    with open(argv[1], 'r', encoding='utf-8') as inp:
        cities = [
            City(
                name=city['name'],
                uri=city['uri'],
                url_en=city['url_en'],
                url_nl=city['url_nl'],
                properties=dict()
            ) for city in json.load(inp)
        ]

    properties_per_city = get_properties_per_city(cities)
    all_properties = create_all_properties_dict(properties_per_city)

    # write properties to file
    with open(argv[2], 'w', encoding='utf-8') as out:
        json.dump(properties_per_city, out, indent=4, default=lambda x: x.to_dict())

    with open(argv[3], 'w', encoding='utf-8') as out:
        json.dump(all_properties, out, indent=4, default=lambda x: x.to_dict())

    print(
        f'Done, properties for {len(properties_per_city)} cities written to file: {argv[2]}',
        file=sys.stderr,
    )

    print(
        f'Done, {len(all_properties)} properties written to file: {argv[3]}',
        file=sys.stderr,
    )


if __name__ == '__main__':
    main(sys.argv)
