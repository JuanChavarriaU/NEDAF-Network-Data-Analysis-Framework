"""
Configuration module for NEDAF.

All paths use environment variables with sensible defaults relative to the project root.
Create a .env file in the project root to customize settings.
"""
import os
from pathlib import Path

# Base directories - relative to project root
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / ".cache"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, CACHE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# LLM and vector store configuration
PERSIST_DIR = Path(os.getenv("NEDAF_VECTOR_STORE", CACHE_DIR / "vectorstore"))
LOGS_FILE = Path(os.getenv("NEDAF_LOGS", LOGS_DIR / "nedaf.log"))
FILE_DIR = Path(os.getenv("NEDAF_BOOKS_DIR", DATA_DIR / "books"))

# Create LLM directories
PERSIST_DIR.mkdir(parents=True, exist_ok=True)
FILE_DIR.mkdir(parents=True, exist_ok=True)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM parameters
K = int(os.getenv("NEDAF_LLM_CHUNKS", "4"))  # number of chunks to consider when generating answer

# LLM prompt template
PROMPT_TEMPLATE = """You are a personal Bot assistant for answering any questions about graph theory, mobility networks, network science, biology and statistics.
You are given a question and a set of documents.
If the user's question requires you to provide specific information from the documents, give your answer based only on the examples provided below. DON'T generate an answer that is NOT written in the provided examples.
If you don't find the answer to the user's question with the examples provided to you below, answer that you didn't find the answer in the documentation and propose him to rephrase his query with more details.
Use bullet points if you have to make a list, only if necessary.

DOCUMENTS:
=========
{context}
=========
Finish by proposing your help for anything else.
"""

# Legacy aliases for backward compatibility
prompt_template = PROMPT_TEMPLATE
k = K