# Minimal RAG Pipeline using Serper.dev, NewsCatcher, and Ollama LLM with Chain of Thought Reasoning

import requests
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import OpenAI
import http.client
import json

# === General Web Search Fetcher (Serper.dev) ===
def fetch_serper(query):
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': '742be761826127dcb585dd274bb3a72cf87b0f11',
        'Content-Type': 'application/json'
    }
    try:
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        return [item['snippet'] for item in data.get("organic", []) if 'snippet' in item]
    except:
        return []

# === News Search Fetcher (NewsCatcher) ===
def fetch_newscatcher(query):
    conn = http.client.HTTPSConnection("newscatcher.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "28ae9a713bmsh1facb6ce4437b3bp1324b9jsn193ad2f41b2b",
        'x-rapidapi-host': "newscatcher.p.rapidapi.com"
    }
    try:
        path = f"/v1/aggregation?q={query}&agg_by=day&media=True"
        conn.request("GET", path, headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        return [item['summary'] for item in data.get("articles", []) if 'summary' in item]
    except:
        return []

# === Embedding & Indexing ===
def create_faiss_index(documents, encoder):
    if not documents:
        return None, None
    doc_embeddings = encoder.encode(documents)
    dim = doc_embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(doc_embeddings))
    return index, doc_embeddings

# === RAG Function with Chain of Thought ===
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

history = []

def rag_query(user_query, documents, encoder, index, top_k=2):
    if not documents:
        return None
    query_embedding = encoder.encode([user_query])
    distances, indices = index.search(np.array(query_embedding), top_k)
    context_docs = [documents[i] for i in indices[0] if i < len(documents)]
    context = "\n---\n".join(context_docs)

    prompt = f"""
"You are a precise and logical assistant designed to answer questions using real-time web and news data. "
    "Your task is to analyze the user's query step-by-step, identify the key intent, and extract the answer strictly from the provided context. "
    "Never make assumptions or introduce information not explicitly present in the context. "
    "If the context lacks enough information to answer the query, respond with:\n"
    "\"The provided information does not contain enough details to answer this question.\"\n"
    "Prioritize clarity, brevity, and factual accuracy in your responses."

Context:
{context}

User Query:
{user_query}
"""

    messages = [
        {"role": "system", "content": "You answer using only the provided context."},
    ]

    for prev_query, prev_answer in history[-3:]:
        messages.append({"role": "user", "content": prev_query})
        messages.append({"role": "assistant", "content": prev_answer})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="mistral",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

# === Main Loop ===
if __name__ == "__main__":
    encoder = SentenceTransformer("all-MiniLM-L6-v2")

    while True:
        user_query = input("Enter your query (or 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break

        # Add disambiguation logic: Use last query if current one is too short
        if len(user_query.split()) < 4 and history:
            user_query = history[-1][0] + " " + user_query

        documents = fetch_serper(user_query)
        index, _ = create_faiss_index(documents, encoder)
        answer = rag_query(user_query, documents, encoder, index)

        if not answer or "don't know" in answer or "not contain enough details" in answer:
            print("Serper did not yield sufficient results. Trying NewsCatcher...")
            documents = fetch_newscatcher(user_query)
            index, _ = create_faiss_index(documents, encoder)
            answer = rag_query(user_query, documents, encoder, index)

        final_answer = answer if answer else "The provided information does not contain enough details to answer this question."
        print("\nGenerated Answer:\n", final_answer)

        history.append((user_query, final_answer))
