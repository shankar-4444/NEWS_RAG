# main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from rag_engine import rag_pipeline  # now uses the pipeline

app = FastAPI()

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def query_endpoint(req: Request):
    data = await req.json()
    query = data.get("query", "")
    answer = rag_pipeline(query)
    return {"answer": answer}
@app.get("/")
def read_root():
    return {"message": "Backend is running. Use POST /query to interact."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
