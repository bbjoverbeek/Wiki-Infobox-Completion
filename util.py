from dataclasses import dataclass
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
