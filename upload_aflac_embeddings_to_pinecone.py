import os
import openai
import pinecone
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load .env file
load_dotenv()

# Get env variables
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

# Instantiate Pinecone client
pc = Pinecone(api_key=pinecone_key)

# Connect to your index
index = pc.Index("aflac-brain")

# Load data
df = pd.read_csv("aflac_chunks.csv", skiprows=1)

# Upload embeddings
for _, row in tqdm(df.iterrows(), total=len(df)):
    chunk_id = row["id"]
    text = row["text"]

    try:
        embedding = openai.Embedding.create(
            input=text,
            model="text-embedding-3-small"
        )["data"][0]["embedding"]

        index.upsert([
            (chunk_id, embedding, {"text": text})
        ])
    except Exception as e:
        print(f"Failed to process chunk {chunk_id}: {e}")
