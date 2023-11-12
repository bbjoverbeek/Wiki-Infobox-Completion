import json
import pprint
import random
from enum import Enum

from config import RANDOM_SEED
from util import InfoBoxCity, EmbeddingComparisonMode
from value_alignment import process_cities
import value_alignment
import embedding_alignment


class CompletionMode(Enum):
    """
    The completion mode for the infoboxes. This can be either all (which includes values alignment
    and using words embeddings to find additional matching properties) or value_alignment (which
    only uses value alignment to find additional matching properties).
    """
    VALUE_ALIGNMENT = "value_alignment"
    ALL = "all"


def complete_infobox(
        mode: CompletionMode,
        cities: list[InfoBoxCity],
        value_alignments: dict[str, str],
        embedding_alignments: dict[str, str] = None
) -> list[InfoBoxCity]:
    for city in cities:
        city.all_alignment_completed_infobox = {}
        city.value_alignment_completed_infobox = {}

        for property_, value in city.infobox_en.items():
            used_value_alignment = False
            if value not in city.infobox_nl.values():
                value_property = value_alignments.get(property_, None)
                if value_property and value_property not in city.infobox_nl.keys():
                    city.value_alignment_completed_infobox[value_property] = value
                    city.all_alignment_completed_infobox[value_property] = value
                    used_value_alignment = True

            if mode == CompletionMode.ALL and not used_value_alignment:
                embedding_property = embedding_alignments.get(property_, None)
                if embedding_property and embedding_property not in city.infobox_nl.keys():
                    city.all_alignment_completed_infobox[embedding_property] = value

    return cities


def main():
    with open("data/infoboxes.json", "r") as file:
        cities = [InfoBoxCity.from_dict(city) for city in json.load(file)]

    value_properties = process_cities(cities)
    value_alignments = value_alignment.align_properties(value_properties)

    embedding_alignments = embedding_alignment.align_properties(
        cities, EmbeddingComparisonMode.EUCLIDEAN
    )

    with open("data/embedding-alignments.json", "w") as file:
        json.dump(embedding_alignments, file, indent=4)

    cities = complete_infobox(
        CompletionMode.ALL, cities, value_alignments, embedding_alignments
    )

    random.seed(RANDOM_SEED)
    test_cities = random.sample(cities, 40)

    with open("data/cities-completed.json", "w") as file:
        json.dump(cities, file, indent=4, default=lambda x: x.to_dict())

    with open("data/test-cities.json", "w") as file:
        json.dump(test_cities, file, indent=4, default=lambda x: x.to_dict())


if __name__ == '__main__':
    main()
