import json
import unicodedata
from dataclasses import dataclass

import requests
import wptools
from bs4 import BeautifulSoup, ResultSet, Tag
import re

from dataclasses_json import dataclass_json
from tqdm import tqdm


@dataclass_json
@dataclass
class City:
    """A city with its name, population, and wikidata URI"""
    name: str
    uri: str
    url_en: str
    url_nl: str
    infobox_en: dict[str, list[str]]
    infobox_nl: dict[str, list[str]]


def get_wiki_page(url: str) -> str:
    headers = {
        'accept': 'text/html; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/HTML/2'
                  '.1.0"'
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return get_wiki_page(url)

    return response.text


def get_html_table_from_page(page: str) -> ResultSet[Tag]:
    soup = BeautifulSoup(page, "lxml")
    table = soup.select("table.infobox")
    return table


def convert_infobox_html_to_dict(table: Tag) -> dict[str, list[str]]:
    """
    Converts the html table to a dictionary. The keys are the table headers, and the values are the
    table data values. Only items where both a table header and table data value are present are
    included.
    :param table: the html table from the wikipedia page
    :return: dictionary with the table headers as keys and the table data values as values in a list
    """
    values = {}

    rows: ResultSet[Tag] = table.find_all('tr')
    for row in rows:
        key_element, value_element = row.find('th'), row.find('td')

        if (
                key_element is not None
                and value_element is not None
                and key_element.text != ""
                and value_element.text != ""
        ):
            values[clean_text(key_element.get_text())] = [
                clean_text(item) for item in value_element.get_text().split("\n") if item != ""
            ]

    return values


REMOVABLE_CHARACTERS = [
    "\ufeff",
    "\xa0",
    "\u200b",
    "\u200e",
    "\u200f",
    "\u202a",
    "\u202c",
    "\u2060",
    "\u25aa",
    "\u25ab",
    "\u25b2",
    "\u25b3",
    "\u25be",
    "\u25bf",
    "•",
]

REMOVEABLE_CHARACTERS_REGEX = re.compile(
    r"(" + "|".join(map(re.escape, REMOVABLE_CHARACTERS)) + ")",
    flags=re.UNICODE
)


def clean_text(value: str) -> str:
    """
    The text that is given by beautiful soup is not always clean. This function tries to remove
    some of the unwanted characters. It will remove references, normalizes the text, and strips it.
    :param value: the text value to clean
    :return: the clean text value
    """
    text = re.sub(r'\[[0-9\w]+]', '', value)
    text = REMOVEABLE_CHARACTERS_REGEX.sub('', text)
    text = unicodedata.normalize("NFKD", text)
    text = text.strip()
    return text


def get_infoboxes(url: str) -> dict[str, list[str]]:
    """
    Get all infoboxes from a wikipedia page.
    :param url: the url of the wikipedia page
    :return: a dictionary with the infoboxes
    """

    # page = wptools.page()
    # page.get_parse()
    # print(url)
    # print(page.data["title"])
    # print(page.data['infobox'])

    page = get_wiki_page(url)
    table = get_html_table_from_page(page)
    if len(table) == 0:
        return {}
    infobox = convert_infobox_html_to_dict(table[0])
    return infobox


def main():
    with open("data/cities.json", "r") as file:
        cities = [
            City(
                name=city['name'],
                uri=city['uri'],
                url_en=city['url_en'],
                url_nl=city['url_nl'],
                infobox_en=None,
                infobox_nl=None,
            )
            for city in json.load(file)
        ]

    for city in tqdm(cities, desc='Getting infoboxes'):
        city.infobox_en = get_infoboxes(city.url_en)
        city.infobox_nl = get_infoboxes(city.url_nl)

    with open("data/infoboxes.json", "w") as file:
        json.dump(cities, file, indent=4, default=lambda x: x.to_dict())


if __name__ == '__main__':
    main()
