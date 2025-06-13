import requests
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import OpenAI
import http.client
import json

encoder = SentenceTransformer("all-MiniLM-L6-v2")
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
history = []

# === Chunking Utility ===
def chunk_text(text, max_tokens=80):
    sentences = text.split('. ')
    chunks, current = [], ""
    for sentence in sentences:
        if len(current.split()) + len(sentence.split()) < max_tokens:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "
    if current:
        chunks.append(current.strip())
    return chunks

# === Web Search Fetcher ===
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
        return [{"text": item['snippet'], "source": item.get("link", "unknown"), "time": "N/A"} for item in data.get("organic", []) if 'snippet' in item]
    except:
        return []

# === NewsCatcher Fetcher ===
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
        return [{"text": item['summary'], "source": item.get("link", "unknown"), "time": item.get("published_date", "N/A")} for item in data.get("articles", []) if 'summary' in item]
    except:
        return []

# === News67 Fetcher ===
def fetch_news67(query):
    url = "https://news67.p.rapidapi.com/news"
    headers = {
        "X-RapidAPI-Key": "3e83b5ecabc24103a33eac0754460b9a",
        "X-RapidAPI-Host": "news67.p.rapidapi.com"
    }
    params = {"q": query, "max": 5}

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return [{"text": item["title"] + ". " + item.get("description", ""), "source": item.get("url", "unknown"), "time": item.get("publishedAt", "N/A")} for item in data.get("articles", [])]
    except:
        return []

# === Embedding & Indexing ===
def create_faiss_index(documents, encoder):
    if not documents:
        return None, None, []
    texts = []
    metadata = []
    for doc in documents:
        chunks = chunk_text(doc['text'])
        for chunk in chunks:
            texts.append(chunk)
            metadata.append((doc['source'], doc['time']))
    embeddings = encoder.encode(texts)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index, embeddings, list(zip(texts, metadata))

# === RAG Core ===
def rag_query(user_query, texts_metadata, encoder, index, top_k=2):
    if not texts_metadata or not index:
        return None
    query_embedding = encoder.encode([user_query])
    distances, indices = index.search(np.array(query_embedding), top_k)
    context_docs = [f"{texts_metadata[i][0]} (source: {texts_metadata[i][1][0]}, time: {texts_metadata[i][1][1]})" for i in indices[0] if i < len(texts_metadata)]
    context = "\n---\n".join(context_docs)

    prompt = f"""
You are a precise and logical assistant designed to answer questions using real-time web and news data.

Think step-by-step to extract key facts, organize them logically, and derive an accurate answer.

Use only the provided context below. If the context lacks enough information, respond with:
"The provided information does not contain enough details to answer this question."

Context:
{context}

User Query:
{user_query}

Now reason step-by-step and answer:
"""

    messages = [
        {"role": "system", "content": "You answer using only the provided context."},
    ]

    for item in history[-3:]:
        messages.append({"role": "user", "content": item["query"]})
        messages.append({"role": "assistant", "content": item["answer"]})

    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="mistral",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("LLM error:", e)
        return None

# === Main Pipeline ===
def rag_pipeline(user_query):
    global history

    if len(user_query.split()) < 4 and history:
        user_query = history[-1]["query"] + " " + user_query

    for fetcher in [fetch_serper, fetch_newscatcher, fetch_news67]:
        documents = fetcher(user_query)
        index, _, texts_metadata = create_faiss_index(documents, encoder)
        answer = rag_query(user_query, texts_metadata, encoder, index)
        if answer and "not contain enough details" not in answer.lower():
            break

    final_answer = answer or "The provided information does not contain enough details to answer this question."
    history.append({"query": user_query, "answer": final_answer, "model": "mistral", "sources": documents})
    return final_answer
