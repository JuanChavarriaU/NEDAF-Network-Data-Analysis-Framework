# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NEDAF (Network Data Analysis Framework) is a Python/PyQt6 desktop application for network data analysis, built as a thesis project. It provides a tabbed interface for importing data, transforming it, exploring statistics, visualizing networks, and querying an LLM for graph-theory insights.

## Commands

```bash
# Run the application
python main.py

# Run unit tests (most test classes in tests.py are currently commented out)
python -m unittest discover -s . -p "test*.py" -v

# Build standalone executable
pyinstaller NEDAF.spec

# Install dependencies
pip install -r requirements.txt
```

## Architecture

**Pattern:** Model-View with a shared DataManager (ViewModel directory exists but is unused).

**Entry point:** `main.py` — creates `MainWindow(QMainWindow)` with a `QTabWidget` holding 5 tabs.

**Data flow:** `DataManager` (Model/) holds the current DataFrame and emits PyQt signals when data changes. Views subscribe to these signals to stay in sync.

### Model Layer (`Model/`)
- **DataManager.py** — Central data store with PyQt signals for cross-tab synchronization
- **NetworkAnalysis.py** — Graph creation (NetworkX), layout algorithms (ForceAtlas2 for large, Spring for medium, Kamada-Kawai for small), statistics, and community detection (static methods)
- **exploreData.py** — Statistical operations (mean, median, variance, correlation, distribution, etc.)
- **transformationData.py** — Data preprocessing (normalization, missing value removal)
- **chatbot.py** — LangChain chains with OpenAI for graph-theory Q&A
- **retriever.py** — ChromaDB document loader for RAG embeddings

### View Layer (`View/`)
- **ImportData.py** — File import (CSV, Parquet, Excel, MTX, Edges formats); includes local and remote (SSH) file browsing
- **TransformationData.py** — UI for data transformations
- **ExploreData.py** — Statistical analysis with visualization
- **NetworkVisualizationMod.py** — Network graph rendering via pyqtgraph; 25+ analysis metrics
- **LLMInsights.py** — Chat interface using QThread for non-blocking LLM calls
- **clusterLogin.py** — SSH cluster connection dialog
- **FileExplorer.py** — Local and remote file browsing widget

## Key Technical Details

- **UI language:** Spanish (labels, tab names, messages)
- **Code comments:** Mixed Spanish/English
- **Threading:** LLM queries run on QThread to keep the UI responsive
- **Network analysis methods** in `NetworkAnalysis.py` are static — they take a NetworkX graph and return results
- **Layout algorithm selection** is size-based: ForceAtlas2 (large graphs), Spring (medium), Kamada-Kawai (small)
- **LLM integration** requires `OPENAI_API_KEY` in a `.env` file
- **Vector store:** ChromaDB persists in `chroma_data/` for RAG-based LLM context

## Dependencies

Core: PyQt6, pandas, numpy, networkx, pyqtgraph, dask, scipy, langchain, langchain-openai, chromadb, paramiko (SSH), fa2_modified (ForceAtlas2), pyarrow

Full dependency list with pinned versions is in `requeriments.txt` (note the typo in filename).
