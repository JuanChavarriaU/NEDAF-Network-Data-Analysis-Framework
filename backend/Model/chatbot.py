"""
Chatbot module for NEDAF LLM insights.

Uses LangChain with OpenAI and ChromaDB for RAG (Retrieval Augmented Generation).
All initialization is lazy to avoid side effects on import.
"""
import os
import dotenv
from langchain_openai import ChatOpenAI 
from langchain_core.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Load environment variables
dotenv.load_dotenv()

BOOKS_CHROMA_PATH = "chroma_data/"

PROMPT_TEMPLATE = """You are a personal Bot assistant for answering any questions about graph theory, mobility networks, network science, biology and statistics.
You are given a question and a set of documents.
If the user's question requires you to provide specific information from the documents, give your answer based only on the examples provided below. DON'T generate an answer that is NOT written in the provided examples.
If you don't find the answer to the user's question with the examples provided to you below, answer that you didn't find the answer in the documentation however propose an answer based on your own knowledge.
Use bullet points if you have to make a list, only if necessary. Based on the language of the input you have to answer in the same language ALWAYS.

DOCUMENTS:
=========
{context}
=========
Finish by proposing your help for anything else.
"""

# Global cache for the chain (lazy initialization)
_book_chain = None


def _get_chain():
    """Lazy initialization of the LangChain RAG chain."""
    global _book_chain

    if _book_chain is not None:
        return _book_chain

    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please create a .env file with your OpenAI API key."
        )

    # Initialize vector database
    book_vector_db = Chroma(
        persist_directory=BOOKS_CHROMA_PATH,
        embedding_function=OpenAIEmbeddings()
    )

    # Build prompt
    book_system_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(input_variables=["context"], template=PROMPT_TEMPLATE)
    )
    book_user_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(input_variables=["question"], template="{question}")
    )
    messages = [book_system_prompt, book_user_prompt]
    book_prompt = ChatPromptTemplate(input_variables=["context", "question"], messages=messages)

    # Build retriever
    book_retriever = book_vector_db.as_retriever(k=3)

    # Build chain
    _book_chain = (
        {
            "context": book_retriever,
            "question": RunnablePassthrough(),
        }
        | book_prompt
        | ChatOpenAI()
        | StrOutputParser()
    )

    return _book_chain


def answer(question: str) -> str:
    """
    Answer a question using RAG with the book knowledge base.

    Args:
        question: The user's question

    Returns:
        The chatbot's answer

    Raises:
        ValueError: If OPENAI_API_KEY is not configured
    """
    chain = _get_chain()
    return chain.invoke(question)
