import unicodedata
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
import pprint
from enum import Enum
import re


class Language(Enum):
    English = "en"
    Dutch = "nl"


def get_wiki_page(language: Language, title: str) -> str:
    url = f'https://{language.value}.wikipedia.org/api/rest_v1/page/html/{title}'
    headers = {
        'accept': 'text/html; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/HTML/2'
                  '.1.0"'
    }
    response = requests.get(url, headers=headers)
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


def clean_text(value: str) -> str:
    """
    The text that is given by beautiful soup is not always clean. This function tries to remove
    some of the unwanted characters. It will remove references, normalizes the text, and strips it.
    :param value: the text value to clean
    :return: the clean text value
    """
    text = re.sub(r'\[[0-9]+]', '', value)
    text = re.sub(r'[\ufeff]', '', text)
    text = unicodedata.normalize("NFKD", text)
    text = text.strip()
    return text


def main():
    page = get_wiki_page(Language.Dutch, "Universiteit Groningen")
    with open("response_university_of_groningen.html", "w") as f:
        f.write(str(page))
    table = get_html_table_from_page(page)[0]
    values = convert_infobox_html_to_dict(table)
    pprint.pprint(values)


if __name__ == '__main__':
    main()
