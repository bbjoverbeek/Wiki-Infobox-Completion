import json
from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CityProperty:
    """A property with its id, and label in English and Dutch"""
    id: str
    label_en: str
    label_nl: str


@dataclass_json
@dataclass
class Property:
    """A property with its id, and label in English and Dutch"""
    id: str
    label_en: str
    label_nl: str

    absolute_frequency: int
    relative_frequency: float


@dataclass
class City:
    """A city with its name, population, and wikidata URI"""
    name: str
    uri: str
    url_en: str
    url_nl: str

    properties: dict[str, CityProperty]


@dataclass_json
@dataclass
class InfoBoxCity:
    """A city with its name, population, and wikidata URI"""
    name: str
    uri: str
    url_en: str
    url_nl: str
    infobox_en: dict[str, list[str]]
    infobox_nl: dict[str, list[str]]

    value_alignment_completed_infobox: dict[str, list[str]] = None
    all_alignment_completed_infobox: dict[str, list[str]] = None



class EmbeddingComparisonMode(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"


def main():
    with open("data/cities.json", "r") as file:
        cities =  json.load(file)
    print(len(cities))


if __name__ == '__main__':
    main()