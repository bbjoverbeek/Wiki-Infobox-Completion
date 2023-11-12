import itertools
import json
from transformers import pipeline
from hugging_face_token import token
import numpy as np

from util import InfoBoxCity, EmbeddingComparisonMode
from config import COSINE_THRESHOLD, EUCLIDEAN_THRESHOLD

pipe = pipeline("feature-extraction", model="xlm-roberta-large", device=0, token=token)


def compute_similarity(
    property_en: str,
    property_nl: str,
    mode: EmbeddingComparisonMode = EmbeddingComparisonMode.EUDLIDEAN,
) -> float:
    """
    Uses the extraction pipeline to extract embeddings for the input strings and computes
    """

    emb1 = np.array(pipe(property_en)).mean(axis=1)
    emb2 = np.array(pipe(property_nl)).mean(axis=1)

    if mode == EmbeddingComparisonMode.COSINE:
        distance = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    elif mode == EmbeddingComparisonMode.EUCLIDEAN:
        distance = np.linalg.norm(emb1 - emb2)
    else:
        raise ValueError(f"Unknown comparison mode {mode}")

    return distance


def get_unique_properties(cities: list[InfoBoxCity]) -> set[str]:
    properties = set()

    for city in cities:
        properties.update(city.infobox_en.keys())

    return properties


def align_properties(
    cities: list[InfoBoxCity], mode: EmbeddingComparisonMode
) -> dict[str, str]:
    alignments = {}

    properties_en = get_unique_properties(cities)
    properties_nl = get_unique_properties(cities)

    for property_en, property_nl in itertools.product(properties_en, properties_nl):
        distance = compute_similarity(property_en, property_nl, mode)

        match (mode, distance > COSINE_THRESHOLD, distance < EUCLIDEAN_THRESHOLD):
            case (EmbeddingComparisonMode.COSINE, True, _) if alignments[
                property_en
            ] is None or alignments[property_en][1] > distance:
                alignments[property_en] = (property_nl, distance)
            case (EmbeddingComparisonMode.EUCLIDEAN, _, True) if alignments[
                property_en
            ] is None or alignments[property_en][1] < distance:
                alignments[property_en] = (property_nl, distance)

    return {key: value[0] for key, value in alignments.items()}


def main():
    with open("data/infoboxes.json", "r") as file:
        cities = [InfoBoxCity.from_dict(city) for city in json.load(file)]


if __name__ == "__main__":
    main()
