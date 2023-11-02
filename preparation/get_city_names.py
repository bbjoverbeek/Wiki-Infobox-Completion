import requests
import json


def get_cities(population_size: int = 125000) -> list[dict[str, dict[str, str]]]:
    """
    With a SPARQL query, get all cities with a population of over 125000. The city name and
    population size are returned.
    :return:
    """
    url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?city ?cityLabel  ?population
    WHERE
    {
      ?city wdt:P31 wd:Q515.
      ?city wdt:P1082 ?population.
      FILTER(?population > """ + str(population_size) + """)
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    headers = {
        'Accept': 'application/sparql-results+json,*/*;q=0.9',
        'User-Agent': 'python-requests/2.24.0',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'query': query,
        'format': 'json'
    }
    response = requests.post(url, headers=headers, data=data)
    result = [
        {
            "name": item['cityLabel']['value'],
            "population": item['population']['value'],
            "uri": item['city']['value']
        }
        for item in response.json()['results']['bindings']
    ]
    return result


def main():
    cities = get_cities(125000)

    with open("../data/cities.json", "w") as file:
        json.dump(cities, file, indent=4)


if __name__ == '__main__':
    main()