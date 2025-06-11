
import os
import openai
import pinecone
from fastapi import FastAPI
from pydantic import BaseModel

# For local development you can use python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

# -----------------------------
# API Keys & Pinecone Setup
# -----------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

if not (openai.api_key and pinecone_key and pinecone_env):
    raise RuntimeError(
        "Environment variables OPENAI_API_KEY, PINECONE_API_KEY, and PINECONE_ENVIRONMENT must be set."
    )

pc = pinecone.Pinecone(api_key=pinecone_key, environment=pinecone_env)
index = pc.Index("aflac-brain")

app = FastAPI()

class Question(BaseModel):
    query: str

def generate_aflac_response(question: str, top_k: int = 5) -> str:
    # Embed the question
    question_embedding = openai.Embedding.create(
        input=question,
        model="text-embedding-3-large"
    )["data"][0]["embedding"]

    # Retrieve from Pinecone
    result = index.query(
        vector=question_embedding,
        top_k=top_k,
        include_metadata=True
    )

    # Build knowledge context
    context = "\n---\n".join([m['metadata']['text'] for m in result['matches']])

    prompt = f"""You are a confident and professional Aflac representative.
Using only the information below, answer the following prospect question or objection in a persuasive and conversational tone:

Knowledge:
{context}

Prospect: {question}
Aflac Representative:"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response['choices'][0]['message']['content']

@app.post("/ask")
async def ask_agent(question: Question):
    answer = generate_aflac_response(question.query)
    return {"response": answer}

@app.get("/health")
async def health():
    return {"ok": True}
