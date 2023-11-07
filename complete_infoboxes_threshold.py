import json
import random
import statistics
import sys

from property_similarity import compute_similarity
from util import Property

random.seed(42)


def find_similarities(all_properties: dict[str, Property]) -> float:
    properties = list(all_properties.values())
    correct_similarities = []
    lowest_incorrect_similarities = []

    for property_ in properties:
        if property_.label_en is None or property_.label_nl is None:
            continue

        similarity = compute_similarity(property_.label_en, property_.label_nl)
        correct_similarities.append(similarity)

        print(property_.label_en, property_.label_nl, similarity)

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





def main():
    with open("data/all-properties.json", "r") as f:
        properties = json.load(f)

    l = len(properties)

    train = {k: Property.from_dict(v) for k, v in list(properties.items())[0:int(l * 0.8)]}
    test = {k: Property.from_dict(v) for k, v in list(properties.items())[int(l * 0.8):]}

    score = find_similarities(train)
    print(score)


if __name__ == '__main__':
    main()
