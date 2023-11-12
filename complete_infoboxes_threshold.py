import json
import random
import statistics

import sklearn
from tqdm import tqdm

from compute_euclidean_distance import compute_similarity
from util import Property

random.seed(42)


def find_similarities(all_properties: dict[str, Property]) -> float:
    properties = list(all_properties.values())
    correct_similarities = []
    lowest_incorrect_similarities = []

    for property_ in tqdm(properties, desc="Finding similarities"):
        if property_.label_en is None or property_.label_nl is None:
            continue

        similarity = compute_similarity(property_.label_en, property_.label_nl)
        correct_similarities.append(similarity)

        incorrect_properties = random.sample(properties, 8)
        incorrect_similarities = []

        for incorrect_property in incorrect_properties:
            if (
                    incorrect_property.label_en is None
                    or incorrect_property.label_nl is None
                    or incorrect_property.label_en == property_.label_en
            ):
                continue

            incorrect_similarity = compute_similarity(
                incorrect_property.label_en, incorrect_property.label_nl
            )

            incorrect_similarities.append(incorrect_similarity)

        incorrect_similarities.sort()
        lowest_incorrect_similarities.extend(incorrect_similarities[0:3])

    mean_lowest_incorrect = statistics.mean(lowest_incorrect_similarities)
    mean_correct = statistics.mean(correct_similarities)

    return statistics.mean([mean_correct, mean_lowest_incorrect])


THRESHOLD = 1.4950442


def testing(
        test_properties: dict[str, Property], threshold: float
) -> tuple[float, float, float, float]:
    properties = list(test_properties.values())
    predictions = []
    labels = []

    for property_ in tqdm(properties, desc="Testing threshold"):
        if property_.label_en is None or property_.label_nl is None:
            continue

        for property_2 in properties:
            if (
                    property_2.label_en is None
                    or property_2.label_nl is None
            ):
                continue

            similarity = compute_similarity(property_.label_en, property_2.label_nl)

            predictions.append(similarity < threshold)
            labels.append(property_.label_en == property_2.label_en)

    return (
        sklearn.metrics.f1_score(labels, predictions),
        sklearn.metrics.precision_score(labels, predictions),
        sklearn.metrics.recall_score(labels, predictions),
        sklearn.metrics.accuracy_score(labels, predictions)
    )


# def get_lowest(input: list[list[]])


# scores
# (0.17120622568093385, 0.12680115273775217, 0.2634730538922156, 0.984725160457528)

def main():
    with open("data/all-properties.json", "r") as f:
        properties = json.load(f)

    l = len(properties)

    train = {k: Property.from_dict(v) for k, v in list(properties.items())[0:int(l * 0.8)]}
    test = {k: Property.from_dict(v) for k, v in list(properties.items())[int(l * 0.8):]}

    # score = find_similarities(train)
    score = testing(test, THRESHOLD)
    print(score)


if __name__ == '__main__':
    main()
