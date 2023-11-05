"""Sorts data/all_properties based on amount of occurences"""
import json


def main():
    with open('./data/all_properties.json', 'r', encoding='utf-8') as inp:
        all_properties = json.load(inp)

    sorted_properties = sorted(
        all_properties.items(), key=lambda x: x[1]['absolute_frequency'], reverse=True
    )

    with open('./data/all_properties_sorted.json', 'w', encoding='utf-8') as outp:
        json.dump(sorted_properties, outp, indent=4)


if __name__ == '__main__':
    main()
