"""Computes the wuclidean distance between all properties in Dutch and English"""
from tqdm import tqdm
import json
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

# Load the model and tokenizer
model_id = 'xlm-roberta-base'
tokenizer = AutoTokenizer.from_pretrained(model_id, device=0)
model = AutoModel.from_pretrained(model_id)


def compute_similarity(
    token1: str,
    token2: str,
    layer: int = -1,
    cosine_similarity: bool = False,
) -> float:
    """Extracts word embeddings from an LLM (default xlm-roberta-base)
    at a given layer and returns their euclidean distance. If cosine_similarity
    is True, returns their cosine similarity.
    """

    # Tokenize the input strings
    inputs1 = tokenizer(token1, return_tensors='pt')
    inputs2 = tokenizer(token2, return_tensors='pt')

    # Extract the embeddings for each string
    with torch.no_grad():
        outputs1 = model(**inputs1, output_hidden_states=True)
        emb1 = outputs1.hidden_states[layer].squeeze().mean(dim=0).numpy()
        outputs2 = model(**inputs2, output_hidden_states=True)
        emb2 = outputs2.hidden_states[layer].squeeze().mean(dim=0).numpy()

    # compute cosine similarity or euclidean distance
    if cosine_similarity:
        distance = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    else:
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
