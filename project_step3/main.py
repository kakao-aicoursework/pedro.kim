import os
import logging
import json

import chromadb
from chromadb.config import Settings

from api import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-16s %(levelname)-8s %(message)s ",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError("OPENAI_API_KEY not defined as an environment variable")

def add_embeddings(chroma_client, collection_name, datafile_name):
    try:
        collections = chroma_client.create_collection(name=collection_name)
    except ValueError as exc:
        return
    with open("../prompt_data/refined_data_for_embedding/index.json") as f:
        doc_index = json.load(f)
    documents = []
    for fn in doc_index[datafile_name]:
        with open(os.path.join("../prompt_data/refined_data_for_embedding/", fn)) as f:
            documents.append(f.read())
    collections.add(
        documents=documents,
        ids=doc_index[datafile_name]
    )

def initialize_vector_db():
    chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
    add_embeddings(chroma_client, "kakaotalk_channel", "project_data_카카오톡채널.json")
    add_embeddings(chroma_client, "kakaosync", "project_data_카카오싱크.json")
    add_embeddings(chroma_client, "kakaosocial", "project_data_카카오소셜.json")

initialize_vector_db()

if __name__ == "__main__":
    pass
