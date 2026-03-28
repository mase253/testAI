from fastapi import FastAPI

# Validates incoming JSON data
# Parses it into Python objects
# Ensures correct types (e.g., str, List, etc.)
from pydantic import BaseModel
from typing import List
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.documents import Document
from dotenv import load_dotenv


load_dotenv()

# this how we create FastAPI
app = FastAPI()


vector_store = None


class IngestRequest(BaseModel):
    file_path: str


class QueryRequest(BaseModel):
    query: str


embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)


# think req as
# {
#   "file_path": "data/sample.pdf"
# }


@app.post("/ingest")
def ingest(req: IngestRequest):
    global vector_store

    loader = PyPDFLoader(req.file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = splitter.split_documents(docs)

    vector_store = Chroma(
        collection_name="rag_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )

    vector_store.add_documents(splits)

    return {"status": "Documents ingested", "chunks": len(splits)}


@app.post("/query")
def query(req: QueryRequest):
    global vector_store

    if vector_store is None:
        return {"error": "No documents ingested yet"}

    results = vector_store.similarity_search(req.query, k=5)

    context = "\n\n".join([doc.page_content for doc in results])

    prompt = f"""
Use ONLY the context below to answer.
If not found, say "I don't know".
 
 
Context:
{context}
 
 
Question:
{req.query}
"""

    response = llm.invoke(prompt)

    return {"answer": response.content, "sources": [doc.metadata for doc in results]}
