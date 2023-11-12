import json
import argparse
from networkx import min_cost_flow_cost
import numpy as np
from tqdm import tqdm
import sys
from complete_infoboxes_threshold import find_similarities

from util import CityProperty, Property, City
from sklearn.metrics import classification_report


def parse_args():
    """Parse the args to determine whether to test the threshold method, or
    robust method, and to test on all properties or properties per city.
    """
    parser = argparse.ArgumentParser()


def test_threshold_per_city():
    """"""
    pass


def test_threshold_all_properties():
    """"""
    pass


def test_robust_per_city(
    prop_per_city: dict[str, dict[str, CityProperty]], from_lang: str, to_lang: str
):
    """Computes the property similarity between all properties of each city,
    and determines which property aligns best witht the other translation"""

    for city_id, city_properties in prop_per_city.items():
        property_map = dict()
        for property_id, property_langs in city_properties.items():
            if property_langs[from_lang] == "":
                continue
            property_map[(property_id, property_langs[from_lang])] = ""

            # compute_similarity(
            #     property_, city_properties[property_], prop_per_city, from_lang, to_lang
            # )

    print(property_map)


def test_robust_properties(properties) -> list[int]:
    """Uses the property embeddings to test the compute_metric function"""
    predictions: list[int] = []

    correct_relative: float = 0.0
    incorrect_relative: float = 0.0

    correct_similarities: list[float] = []
    incorrect_similarities: list[float] = []

    for property_id, value in tqdm(properties.items()):
        similarities = {
            pid: compute_similarity(value["emb_nl"], val["emb_en"])
            for pid, val in properties.items()
        }
        if min(similarities, key=similarities.get) == property_id:
            predictions.append(1)
            correct_relative += properties[property_id]["relative_frequency"]
            correct_similarities.append(min(similarities.values()))
        else:
            predictions.append(0)
            incorrect_relative += properties[property_id]["relative_frequency"]
            incorrect_similarities.append(min(similarities.values()))

    print(f"Correct relative: {correct_relative}")
    print(f"Incorrect relative: {incorrect_relative}")

    print(f"highest correct similarity: {max(correct_similarities)}")
    print(f"average correct similarity: {np.mean(correct_similarities)}")

    print(f"lowest incorrect similarity: {min(incorrect_similarities)}")
    print(f"average incorrect similarity: {np.mean(incorrect_similarities)}")

    return predictions


def compute_similarity(emb1: list[float], emb2: list[float]) -> float:
    """Computes the similarity between two embeddings"""
    # convert lists to np arrays
    emb1 = np.array(emb1)
    emb2 = np.array(emb2)

    # cosine similarity
    # similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    # euclidean distance
    similarity = np.linalg.norm(emb1 - emb2)

    return similarity


def find_threshold(properties: dict[str, dict], precision: float) -> float:
    """Finds the euclidean distance threshold where the precision is at least the given precision"""
    # create similarity mapping:
    similarity_mapping = dict()
    for property_id1, value1 in tqdm(
        properties.items(), leave=False, desc="creating similarity mapping"
    ):
        similarity_mapping[property_id1] = dict()
        for property_id2, value2 in properties.items():
            similarity_mapping[property_id1][property_id2] = compute_similarity(
                value1["emb_nl"], value2["emb_en"]
            )

    return threshold


def main(argv: list[str]):
    """Tests the property similarity method in two different ways: robust and
    threshold.
    """
    # with open('data/properties-per-city.json', 'r', encoding='utf-8') as inp:
    #     prop_per_city = json.load(inp)

    with open(argv[1], "r", encoding="utf-8") as inp:
        all_properties = json.load(inp)

    # test_robust_per_city(prop_per_city, from_lang='en', to_lang='nl')

    # predictions = test_robust_properties(all_properties)

    # print()
    # print(
    #     classification_report(
    #         [1 for x in range(len(predictions))], predictions, zero_division=0
    #     ),
    # )

    threshold = find_threshold(all_properties, 0.8)
    print(f"Found threshold: {threshold}")


if __name__ == "__main__":
    main(sys.argv)
