import itertools
import json
from enum import Enum

from tqdm import tqdm
from transformers import pipeline
import numpy as np

from util import InfoBoxCity, EmbeddingComparisonMode
from config import COSINE_THRESHOLD, EUCLIDEAN_THRESHOLD, MODEL_NAME

pipe = pipeline("feature-extraction", model=MODEL_NAME, device=0)


def compute_similarity(
        property_en: str,
        property_nl: str,
        mode: EmbeddingComparisonMode = EmbeddingComparisonMode.EUCLIDEAN,
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


class Language(Enum):
    EN = "en"
    NL = "nl"


def get_unique_properties(cities: list[InfoBoxCity], language: Language) -> set[str]:
    properties = set()

    for city in cities:
        if language == Language.EN:
            properties.update(city.infobox_en.keys())
        elif language == Language.NL:
            properties.update(city.infobox_nl.keys())
        else:
            raise ValueError(f"Unknown language {language}")

    return properties


def align_properties(
        cities: list[InfoBoxCity], mode: EmbeddingComparisonMode
) -> dict[str, str]:
    alignments = {}

    properties_en = get_unique_properties(cities, Language.EN)
    properties_nl = get_unique_properties(cities, Language.NL)

    for property_en, property_nl in tqdm(
            itertools.product(properties_en, properties_nl),
            total=len(properties_en) * len(properties_nl),
            desc='Aligning properties with embeddings'
    ):
        distance = compute_similarity(property_en, property_nl, mode)

        if mode == EmbeddingComparisonMode.COSINE and distance > COSINE_THRESHOLD:
            if alignments.get(property_en, None) is None or alignments[property_en][1] < distance:
                alignments[property_en] = (property_nl, distance)
        elif mode == EmbeddingComparisonMode.EUCLIDEAN and distance < EUCLIDEAN_THRESHOLD:
            if alignments.get(property_en, None) is None or alignments[property_en][1] > distance:
                alignments[property_en] = (property_nl, distance)

    return {key: value[0] for key, value in alignments.items()}


def main():
    with open("data/infoboxes.json", "r") as file:
        cities = [InfoBoxCity.from_dict(city) for city in json.load(file)]


if __name__ == "__main__":
    main()
