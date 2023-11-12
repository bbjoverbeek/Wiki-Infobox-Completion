"""Extracts the embeddings for all properties in Dutch and English in the fetched infoboxes (all-properties.json)"""
from tqdm import tqdm
import json
import numpy as np
from transformers import pipeline
import warnings
from config import MODEL_NAME

warnings.filterwarnings("ignore")

# define types
Embedding = np.ndarray[float]

# Load the model and tokenizer
pipe = pipeline("feature-extraction", model=MODEL_NAME, device=0)


def extract_mean_embedding(token: str) -> Embedding:
    """Use pipe to extract word embedding for token. Take everage if result
    is multiple embeddings.
    """

    embedding = np.array(pipe(token)).mean(axis=1).squeeze()

    return embedding


def extract_all_embeddings(all_properties: dict[str, dict]) -> dict[str, dict]:
    """Supplements the all_properties dict with embeddings for the properties"""

    for property_id in tqdm(all_properties):
        # extract mean of embeddings
        all_properties[property_id]["emb_nl"] = list(
            extract_mean_embedding(all_properties[property_id]["label_nl"])
        )
        all_properties[property_id]["emb_en"] = list(
            extract_mean_embedding(all_properties[property_id]["label_en"])
        )

    return all_properties


def main():
    """Extracts embeddings for all properties in all-properties.json"""
    with open("data/all-properties.json", "r", encoding="utf-8") as inp:
        all_properties = json.load(inp)

    all_properties_emb = extract_all_embeddings(all_properties)
    with open("data/all-properties-with-emb.json", "w", encoding="utf-8") as outp:
        json.dump(all_properties_emb, outp, indent=4)

    print("Done!")


if __name__ == "__main__":
    main()
