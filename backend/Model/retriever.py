"""
Vector store initialization module for NEDAF LLM features.

This module provides functionality to ingest PDF documents and create
a ChromaDB vector store for RAG (Retrieval Augmented Generation).

Run this script explicitly to initialize or update the vector store:
    python -m ViewModel.retriever
"""
import os
import dotenv
from pathlib import Path
from langchain.document_loaders.directory import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from ViewModel.config import FILE_DIR, PERSIST_DIR

dotenv.load_dotenv()

# Use config paths (with env var support)
BOOKS_FILE_PATH = str(FILE_DIR)
BOOKS_CHROMA_PATH = str(PERSIST_DIR)


def initialize_vector_store(books_path: str = BOOKS_FILE_PATH,
                           chroma_path: str = BOOKS_CHROMA_PATH,
                           force_reload: bool = False) -> Chroma:
    """
    Initialize the vector store from PDF documents.

    Args:
        books_path: Directory containing PDF files
        chroma_path: Directory to store the ChromaDB vector database
        force_reload: If True, rebuild the vector store even if it exists

    Returns:
        The initialized Chroma vector store

    Raises:
        ValueError: If OPENAI_API_KEY is not set
        FileNotFoundError: If books_path doesn't exist or contains no PDFs
    """
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please create a .env file with your OpenAI API key."
        )

    # Check if books directory exists
    books_dir = Path(books_path)
    if not books_dir.exists():
        raise FileNotFoundError(
            f"Books directory not found: {books_path}. "
            f"Create it and add PDF files, or set NEDAF_BOOKS_DIR in .env"
        )

    # Check if vector store already exists
    chroma_dir = Path(chroma_path)
    if chroma_dir.exists() and not force_reload:
        print(f"Vector store already exists at {chroma_path}. Use force_reload=True to rebuild.")
        return Chroma(
            persist_directory=chroma_path,
            embedding_function=OpenAIEmbeddings()
        )

    # Load PDFs
    print(f"Loading PDF documents from {books_path}...")
    loader = DirectoryLoader(books_path, glob="**/*.pdf")
    documents = loader.load_and_split()

    if not documents:
        raise FileNotFoundError(
            f"No PDF files found in {books_path}. "
            f"Add PDF documents to use LLM features."
        )

    print(f"Loaded {len(documents)} document chunks")

    # Create vector store
    print(f"Creating vector store at {chroma_path}...")
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=OpenAIEmbeddings(),
        persist_directory=chroma_path,
    )

    print("Vector store initialized successfully!")
    return vector_db


if __name__ == "__main__":
    """Run this script to initialize the vector store."""
    import sys

    print("=" * 60)
    print("NEDAF Vector Store Initialization")
    print("=" * 60)

    try:
        force = "--force" in sys.argv
        if force:
            print("Force reload enabled - rebuilding vector store...")

        vector_db = initialize_vector_store(force_reload=force)
        print("\n✓ Vector store ready for use!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)