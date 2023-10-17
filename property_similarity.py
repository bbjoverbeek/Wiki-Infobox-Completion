"""
Computes the cosine similarity between two properties using word embeddings
from a pre-trained model to determine if they are the same property in a
different language.
"""
import sys
import numpy as np
from transformers import pipeline
import torch
from transformers import AutoTokenizer, AutoModel


def compute_similarity(
    token1: str,
    token2: str,
    model_id: str = 'xlm-roberta-base',
    layer: int = -1,
    cosine_similarity: bool = False,
) -> float:
    """Extracts word embeddings from an LLM (default xlm-roberta-base)
    at a given layer and returns their euclidean distance. If cosine_similarity
    is True, returns their cosine similarity.
    """

    # Load the model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModel.from_pretrained(model_id)

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


def main(argv: list[str]):
    """Provide two strings as arguments to compute their similarity."""
    word1 = argv[1]
    word2 = argv[2]
    layer = int(argv[3]) if len(argv) == 4 else -1

    similarity = compute_similarity(word1, word2, layer=layer)

    print(
        f'The euclidean distance between \'{word1}\' and \'{word2}\' is'
        + f' {similarity:.5f} at layer {layer}'
    )


if __name__ == '__main__':
    main(sys.argv)
