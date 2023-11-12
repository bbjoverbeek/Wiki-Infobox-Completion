import json
import pprint
import random
from enum import Enum

from config import RANDOM_SEED
from util import InfoBoxCity, EmbeddingComparisonMode, Alignment
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
        city.embedding_alignment_completed_infobox = []
        city.value_alignment_completed_infobox = []

        for property_, value in city.infobox_en.items():
            used_value_alignment = False
            if value not in city.infobox_nl.values():
                value_property = value_alignments.get(property_, None)
                if value_property and value_property not in city.infobox_nl.keys():
                    alignment = Alignment(property_, value_property, value)
                    city.value_alignment_completed_infobox.append(alignment)
                    used_value_alignment = True

            if mode == CompletionMode.ALL and not used_value_alignment:
                embedding_property = embedding_alignments.get(property_, None)
                if embedding_property and embedding_property not in city.infobox_nl.keys():
                    alignment = Alignment(property_, embedding_property, value)
                    city.embedding_alignment_completed_infobox.append(alignment)

    return cities


def main():
    population = 125000
    use_embedding_alignments_file = True

    with open(f"data/infoboxes_{population}.json", "r") as file:
        cities = [InfoBoxCity.from_dict(city) for city in json.load(file)]

    value_properties = process_cities(cities)
    value_alignments = value_alignment.align_properties(value_properties)

    with open(f"data/value-alignments_{population}.json", "w") as file:
        json.dump(value_alignments, file, indent=4)

    population = 250000
    if use_embedding_alignments_file:
        with open(f"data/embedding-alignments_{population}.json", "r") as file:
            embedding_alignments = json.load(file)
    else:
        with open(f"data/value-alignments_{population}.json", "r") as file:
            embedding_cities = [InfoBoxCity.from_dict(city) for city in json.load(file)]

        embedding_alignments = embedding_alignment.align_properties(
            embedding_cities, EmbeddingComparisonMode.EUCLIDEAN
        )

        with open(f"data/embedding-alignments_{population}.json", "w") as file:
            json.dump(embedding_alignments, file, indent=4)

    cities = complete_infobox(
        CompletionMode.ALL, cities, value_alignments, embedding_alignments
    )

    random.seed(RANDOM_SEED)
    test_cities = random.sample(cities, 40)

    with open(f"data/cities-completed_{population}.json", "w") as file:
        json.dump(cities, file, indent=4, default=lambda x: x.to_dict())

    with open(f"data/test-cities_{population}.json", "w") as file:
        json.dump(test_cities, file, indent=4, default=lambda x: x.to_dict())


if __name__ == '__main__':
    main()
