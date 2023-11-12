import json
import pprint

from util import InfoBoxCity


def main():
    names = ["Rina", "Sijbren", "Bjorn", "Oscar"]
    verified_cities = []
    for name in names:
        with open(f"data/test-cities_{name}.json", "r") as file:
            cities = [InfoBoxCity.from_dict(city) for city in json.load(file)]
            verified_cities.extend(cities)

    total_value_alignment = 0
    correct_value_alignment = 0

    total_embedding_alignment = 0
    correct_embedding_alignment = 0

    for city in verified_cities:
        total_value_alignment += len(city.value_alignment_completed_infobox)
        total_embedding_alignment += len(city.embedding_alignment_completed_infobox)

        for alignment in city.value_alignment_completed_infobox:
            if alignment.correct:
                correct_value_alignment += 1

        for alignment in city.embedding_alignment_completed_infobox:
            if alignment.correct:
                correct_embedding_alignment += 1

    print(f"Value alignment: {correct_value_alignment}/{total_value_alignment}")
    print(f"Embedding alignment: {correct_embedding_alignment}/{total_embedding_alignment}")


if __name__ == '__main__':
    main()
