"""Computes the Euclidean distance between all properties in Dutch and English"""
from tqdm import tqdm
import json
import numpy as np
from transformers import pipeline, AutoTokenizer
import warnings

warnings.filterwarnings("ignore")

# define types
Embedding = np.ndarray[float]

# Load the model and tokenizer
pipe = pipeline("feature-extraction", model="xlm-roberta-base", device=0, token=token)
tokenizer = AutoTokenizer.from_pretrained("facebook/m2m100_418M")


def extract_mean_embedding(token: str) -> Embedding:
    """Use pipe to extract word embedding for token. Take everage if result
    is multiple embeddings.
    """

    inputs = tokenizer(token, return_tensors="pt")
    inputs["decoder_input_ids"] = inputs["input_ids"]

    embedding = np.array(pipe(token)).mean(axis=1).squeeze()

    # embedding = np.array(pipe(token)).mean(axis=1).squeeze()

    return embedding


def extract_all_embeddings(all_properties: dict[str, dict]) -> dict[str, dict]:
    """Supplements the all_properties dict with embeddings for the properties"""

    for property_id in tqdm(all_properties):
        # extract full embeddgins
        # all_properties[property_id]['emb_nl_full'] = pipe(all_properties[property_id]['label_nl'])
        # all_properties[property_id]['emb_en_full'] = pipe(all_properties[property_id]['label_en'])

        # extract mean of embeddings
        all_properties[property_id]["emb_nl"] = list(
            extract_mean_embedding(all_properties[property_id]["label_nl"])
        )
        all_properties[property_id]["emb_en"] = list(
            extract_mean_embedding(all_properties[property_id]["label_en"])
        )

    return all_properties


def compute_similarity(
    token1: str,
    token2: str,
) -> float:
    """Extracts word embeddings from a LLM and returns their Euclidean distance."""

    # Get embeddings for the input strings
    emb1 = extract_embedding(token1)
    emb2 = extract_embedding(token2)

    # euclidean distance
    # distance = np.linalg.norm(emb1 - emb2)

    # Euclidean similarity
    distance = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    return distance


def create_similarity_mapping(
    all_properties: dict[str, dict]
) -> dict[str, dict[str, float]]:
    """Creates a map of all similarities between all the embeddings"""

    euclidean_dist_mapping = dict()

    for property_id1, value1 in tqdm(all_properties.items(), leave=False):
        euclidean_dist_mapping[property_id1] = dict()
        for property_id2, value2 in tqdm(all_properties.items(), leave=False):
            euclidean_dist_mapping[property_id1][property_id2] = compute_similarity(
                value1["label_en"], value2["label_nl"]
            )

    return euclidean_dist_mapping


def main():
    with open("data/all-properties.json", "r", encoding="utf-8") as inp:
        all_properties = json.load(inp)

    # euclidean_dist_mapping = create_similarity_mapping(all_properties)
    # with open('data/all-properties-cossim.json', 'w', encoding='utf-8') as outp:
    #     json.dump(euclidean_dist_mapping, outp, indent=4)

    all_properties_emb = extract_all_embeddings(all_properties)
    with open("data/all-properties-with-emb.json", "w", encoding="utf-8") as outp:
        json.dump(all_properties_emb, outp, indent=4)

    print("Done!")


if __name__ == "__main__":
    main()
