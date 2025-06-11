
import os
import openai
import pinecone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

# -----------------------------
# API Key & Pinecone Setup
# -----------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

if not (openai.api_key and pinecone_key and pinecone_env):
    raise RuntimeError("Missing environment variables: OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT")

pc = pinecone.Pinecone(api_key=pinecone_key, environment=pinecone_env)
index = pc.Index("aflac-brain")

def get_rag_response(question: str, top_k: int = 5) -> str:
    # Embed the question
    q_emb = openai.Embedding.create(
        input=question,
        model="text-embedding-3-large"
    )["data"][0]["embedding"]

    # Retrieve top matches
    result = index.query(
        vector=q_emb,
        top_k=top_k,
        include_metadata=True
    )

    # Build knowledge context
    context = "\n---\n".join([m['metadata']['text'] for m in result['matches']])

    prompt = f"""You are a confident and professional Aflac representative.
Using only the information below, answer the following question or objection in a persuasive and conversational tone:

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

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    sample_question = "We already offer health benefits, why would we need Aflac?"
    print(get_rag_response(sample_question))
