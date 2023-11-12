import json
from tqdm import tqdm
from util import CityProperty
from compute_threshold import create_similarity_mapping

SimilarityMapping = dict[str, dict[str, float]]


def compute_similarities_per_city(
    prop_per_city: dict[str, dict[str, CityProperty]],
    similarity_mapping: SimilarityMapping,
) -> dict[str, SimilarityMapping]:
    """Creates a similarity mapping per city"""

    similarity_mapping_per_city = dict()

    for city_id, city in prop_per_city.items():
        similarity_mapping_per_city[city_id] = dict()
        for property_id1, value1 in city.items():
            similarity_mapping_per_city[city_id][property_id1] = dict()
            for property_id2, value2 in city.items():
                similarity_mapping_per_city[city_id][property_id1][
                    property_id2
                ] = similarity_mapping[property_id1][property_id2]

    return similarity_mapping_per_city


def test_per_city(
    prop_per_city: dict[str, dict[str, CityProperty]],
    similarity_mapping: SimilarityMapping,
):
    """Tests the word embeddings per city, and returns the sum of all cities"""
    similarities_per_city = compute_similarities_per_city(
        prop_per_city, similarity_mapping
    )

    sum_positions = {idx: 0 for idx in range(1, len(similarity_mapping) + 1)}

    for city, similarities in tqdm(similarities_per_city.items(), leave=False):
        city_positions = test_all_properties(similarities)
        for key in city_positions:
            sum_positions[key] += city_positions[key]

    # print(sum(sum_positions.values()))

    return sum_positions


def test_all_properties(similarity_mapping: SimilarityMapping) -> dict[int, int]:
    """Uses the property embeddings to rank all the similarities"""

    positions = {idx: 0 for idx in range(1, len(similarity_mapping) + 1)}

    for property_id, value in similarity_mapping.items():
        # sort by embedding similarity
        ordered = sorted(value, key=value.get)
        position = ordered.index(property_id) + 1
        positions[position] = positions.get(position, 0) + 1

    return positions


def main():
    """Tests the extracted word embeddings extracted from all-properties.json"""

    with open("./data/all-properties-with-emb.json", "r", encoding="utf-8") as inp:
        all_properties = json.load(inp)
    with open("./data/properties-per-city.json", "r", encoding="utf-8") as inp:
        properties_per_city = json.load(inp)

    try:
        with open("./data/similarity-mappings.json", "r", encoding="utf-8") as inp:
            similarity_mapping = json.load(inp)
    except FileNotFoundError:
        similarity_mapping = create_similarity_mapping(all_properties)
        with open("./data/similarity-mappings.json", "w", encoding="utf-8") as out:
            json.dump(similarity_mapping, out)

    positions = test_all_properties(similarity_mapping)
    positions_city_sum = test_per_city(properties_per_city, similarity_mapping)

    print("These are the positions of all the similarities:")
    print(positions)

    print("---" * 20)

    print("These are the positions of all the similarities:")
    print(positions_city_sum)


if __name__ == "__main__":
    main()
