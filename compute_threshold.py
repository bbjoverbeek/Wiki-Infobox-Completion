from sklearn.metrics import precision_score
import json
from config import MODEL_NAME
import numpy as np


def compute_similarity(emb1: list[float], emb2: list[float]) -> float:
    """Computes the similarity between two embeddings"""
    # convert lists to np arrays
    emb1 = np.array(emb1)
    emb2 = np.array(emb2)

    # compute euclidean distance
    similarity = np.linalg.norm(emb1 - emb2)

    return similarity


def create_similarity_mapping(
    properties: dict[str, dict]
) -> dict[str, dict[str, float]]:
    """Computes the similarity between all property embeddings"""

    similarity_mapping = dict()
    for property_id1, value1 in tqdm(
        properties.items(), leave=False, desc="creating similarity mapping"
    ):
        similarity_mapping[property_id1] = dict()
        for property_id2, value2 in properties.items():
            similarity_mapping[property_id1][property_id2] = compute_similarity(
                value1["emb_nl"], value2["emb_en"]
            )

    # {
    #     "P31": {
    #         "P23": 0.012314,
    #         "P31": 0.0013
    #      }
    # }

    return similarity_mapping


def find_threshold(
    similarity_mapping: dict[str, dict[str, float]],
    min_precision: float,
    increment: float = 0.005,
) -> float:
    """Finds the highest similarity threshold that has a minimum precision of
    min_precision
    """
    # create similarity mapping:

    threshold = 0.0
    precision = 1.0

    while precision > min_precision:
        prev_threshold = threshold
        threshold += increment
        labels = []
        predictions = []
        for property_id1, similarities in similarity_mapping.items():
            for property_id2, similarity in similarities.items():
                labels.append(property_id1 == property_id2)
                predictions.append(similarity < threshold)

        precision = precision_score(labels, predictions, zero_division=0)
        print(f"precision: {precision:.3f} with threshold: {threshold:.3f}")

    return prev_threshold


def main():
    """Find the threshold for euclidean distance between embeddings.
    Comment/uncomment saving/load of similarity mapping to save time."""
    with open("./data/all-properties-with-emb.json", "r", encoding="utf-8") as inp:
        all_properties = json.load(inp)

    similarity_mapping = create_similarity_mapping(all_properties)
    with open("./data/similarity-mappings.json", "w", encoding="utf-8") as out:
        json.dump(similarity_mapping, out)

    # with open(f"./data/similarity-mappings.json", "r", encoding="utf-8") as inp:
    #     similarity_mapping = json.load(inp)

    threshold = find_threshold(similarity_mapping, 0.8, 0.001)
    print(f"Found threshold: {threshold:.3f}")


if __name__ == "__main__":
    main()
