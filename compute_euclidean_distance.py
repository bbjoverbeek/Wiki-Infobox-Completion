"""Computes the wuclidean distance between all properties in Dutch and English"""
from tqdm import tqdm
import json
import numpy as np
from transformers import pipeline

# Load the model and tokenizer
pipe = pipeline('feature-extraction', model='xlm-roberta-base', device=0)


def compute_similarity(
    token1: str,
    token2: str,
) -> float:
    """Extracts word embeddings from an LLM (default xlm-roberta-base)
    at a given layer and returns their euclidean distance. If cosine_similarity
    is True, returns their cosine similarity.
    """

    # Get embeddings for the input strings
    emb1 = np.array(pipe(token1)).mean(axis=1)
    emb2 = np.array(pipe(token2)).mean(axis=1)

    distance = np.linalg.norm(emb1 - emb2)

    return distance


def main():
    with open('data/all-properties.json', 'r', encoding='utf-8') as inp:
        all_properties = json.load(inp)

    euclidean_dist_mapping = dict()

    for property_id1, value1 in tqdm(all_properties.items()):
        euclidean_dist_mapping[(property_id1, value1['label_en'])] = dict()
        for property_id2, value2 in tqdm(all_properties.items()):
            euclidean_dist_mapping[(property_id1, value1['label_en'])][
                (property_id2, value2['label_nl'])
            ] = compute_similarity(value1['label_en'], value2['label_nl'])

    with open('data/all-properties-dist.json', 'r', encoding='utf-8') as outp:
        json.dump(euclidean_dist_mapping, outp, indent=4)


if __name__ == '__main__':
    main()
