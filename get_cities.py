import pprint

import requests
import json


def get_cities(population_size: int = 125000) -> list[dict[str, dict[str, str]]]:
    """
    With a SPARQL query, get all cities with a population of over 125000. The city name and
    population size are returned.
    :return:
    """
    url = "https://query.wikidata.org/sparql"
    query = f"""
    prefix schema: <http://schema.org/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT DISTINCT ?cid ?city ?article_en ?article_nl
    WHERE {{
        ?cid wdt:P31 wd:Q515 .
        ?cid wdt:P1082 ?population .
        ?cid rdfs:label ?city filter (lang(?city) = "en") .
        ?article_en schema:about ?cid .
        ?article_en schema:inLanguage "en" .
        ?article_nl schema:about ?cid .
        ?article_nl schema:inLanguage "nl"
        FILTER (
            SUBSTR(str(?article_en), 1, 25) = "https://en.wikipedia.org/" 
            && SUBSTR(str(?article_nl), 1, 25) = "https://nl.wikipedia.org/"
            && ?population > {population_size}
        )
    }} 
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
            "uri": item['cid']['value'],
            "name": item['city']['value'],
            "url_en": item['article_en']['value'],
            "url_nl": item['article_nl']['value']
        }
        for item in response.json()['results']['bindings']
    ]
    return result


def main():
    population = 1_000_000
    cities = get_cities(population)
    with open(f"data/cities_{population}.json", "w") as file:
        json.dump(cities, file, indent=4)


if __name__ == '__main__':
    main()
