"""Computes the wuclidean distance between all properties in Dutch and English"""
from tqdm import tqdm
import json
import numpy as np
from transformers import pipeline
import warnings

warnings.filterwarnings('ignore')

# Load the model and tokenizer
pipe = pipeline('feature-extraction', model='xlm-roberta-base', device=0)


def compute_similarity(
    token1: str,
    token2: str,
) -> float:
    """Extracts word embeddings from an LLM and returns their euclidean distance."""

    # Get embeddings for the input strings
    emb1 = np.array(pipe(token1)).mean(axis=1)
    emb2 = np.array(pipe(token2)).mean(axis=1)

    distance = np.linalg.norm(emb1 - emb2)

    return distance


def main():
    with open('data/all-properties.json', 'r', encoding='utf-8') as inp:
        all_properties = json.load(inp)

    euclidean_dist_mapping = dict()

    for property_id1, value1 in tqdm(all_properties.items(), leave=False):
        euclidean_dist_mapping[property_id1] = dict()
        for property_id2, value2 in tqdm(all_properties.items(), leave=False):
            euclidean_dist_mapping[property_id1][property_id2] = compute_similarity(
                value1['label_en'], value2['label_nl']
            )

    with open('data/all-properties-dist.json', 'w', encoding='utf-8') as outp:
        json.dump(euclidean_dist_mapping, outp, indent=4)

    print('Done!')


if __name__ == '__main__':
    main()
