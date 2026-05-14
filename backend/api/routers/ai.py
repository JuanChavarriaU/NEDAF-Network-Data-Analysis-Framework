from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.state import app_state
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import os
import json

router = APIRouter()

# Read the Ollama host from environment or default to localhost
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

class InsightRequest(BaseModel):
    question: str
    include_graph_metrics: bool = True

@router.post("/insights")
def get_insights(req: InsightRequest):
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded in the application.")

    # Collect context if requested
    context_str = "No graph context provided."
    if req.include_graph_metrics:
        # We can extract some basic stats to feed the LLM
        num_rows = data.height
        num_cols = data.width
        columns = data.columns
        
        context_str = f"The dataset has {num_rows} rows and {num_cols} columns.\n"
        context_str += f"Columns: {', '.join(columns)}\n"
        # If there are graph metrics available in the state, we can append them
        graph_metrics = app_state.get_graph_metrics()
        if graph_metrics:
            context_str += f"Graph Metrics: {json.dumps(graph_metrics)}\n"

    # Define the SLM Model
    try:
        # The user requested phi3:mini or qwen2:0.6b, phi3:mini is set as default.
        llm = Ollama(base_url=OLLAMA_HOST, model="phi3:mini")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Ollama: {str(e)}")

    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are an expert in graph theory and data analysis.
Use the following context about the loaded dataset and graph to answer the user's question.

Context:
{context}

Question:
{question}

Answer:"""
    )

    try:
        prompt = prompt_template.format(context=context_str, question=req.question)
        response = llm.invoke(prompt)
        return {"response": response, "context_used": req.include_graph_metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
