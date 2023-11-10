import itertools
import json

from util import InfoBoxCity


def process_city(
        properties: dict[str, dict[str, int]], city: InfoBoxCity
) -> dict[str, dict[str, int]]:
    for (key_en, value_en), (key_nl, value_nl) \
            in itertools.product(city.infobox_en.items(), city.infobox_nl.items()):

        if value_en == value_nl:
            if properties.get(key_en, None):
                if properties[key_en].get(key_nl, None):
                    properties[key_en][key_nl] += 1
                else:
                    properties[key_en][key_nl] = 1
            else:
                properties[key_en] = {key_nl: 1}

    return properties


def process_cities(cities: list[InfoBoxCity]) -> dict[str, dict[str, int]]:
    properties = {}

    for city in cities:
        properties = process_city(properties, city)

    return properties


def align_properties(properties: dict[str, dict[str, int]]) -> dict[str, str]:
    alignments = {}

    for key_en, value in properties.items():
        key_nl = max(value, key=value.get)
        alignments[key_en] = key_nl

    return alignments


def get_unique_properties(cities: list[InfoBoxCity]) -> tuple[set[str], set[str]]:
    properties_en = set()
    properties_nl = set()

    for city in cities:
        properties_en.update(city.infobox_en.keys())
        properties_nl.update(city.infobox_nl.keys())

    return properties_en, properties_nl


def main():
    with open("data/infoboxes.json", "r") as file:
        cities = [InfoBoxCity.from_dict(city) for city in json.load(file)]

    properties = process_cities(cities)
    alignments = align_properties(properties)

    print(alignments)

    unique_en, unique_nl = get_unique_properties(cities)
    print("unique_en: ", len(unique_en), "unique_nl: ", len(unique_nl), "alignments: ", len(alignments))


if __name__ == '__main__':
    main()
