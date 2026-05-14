---
name: NEDAF Project Architecture
description: App structure, module responsibilities, data flow, and key design patterns in NEDAF
type: project
---

# NEDAF Architecture Overview

## Entry Point
- `main.py`: Creates `MainWindow(QMainWindow)`, builds a `QTabWidget` with 5 tabs (South position), instantiates one shared `DataManager` passed to each tab.

## Module Layout
```
Model/
  data_manager.py     — DataManager(QObject): holds the DataFrame, emits data_loaded signal
  DataManager.py      — Duplicate of data_manager.py (two versions coexist, causing import confusion)
  explore_logic.py    — exploreData class: pure pandas stat calculations
  NetworkAnalysis.py  — NetworkAnalysis, networkStatistics, NetworkCommunities classes
  transformation_logic.py — TransformationData: dropna, min-max normalize
  chatbot.py          — LangChain RAG chatbot (lazy-initialized OpenAI chain)
  retriever.py        — (not fully read, part of RAG stack)
  exploreData.py      — (old location, now replaced by explore_logic.py)

View/
  import_data_view.py     — ImportData: file dialog, preview table, local/SSH file explorer
  explore_data_view.py    — ExploreData (NEW version): stats exploration with pyqtgraph bar chart
  ExploreData.py          — ExploreData (OLD version with merge conflict markers — still present)
  transform_data_view.py  — TransformationDataWindow: checkboxes for dropna/normalize
  network_visualization.py — NetworkVisualizationMod: graph rendering with PyQtGraph + threading
  llm_insights_view.py    — LLMInsights: chat UI calling chatbot.answer() synchronously
  FileExplorer.py         — Local + SSH file tree widget
  clusterLogin.py         — SSH cluster login dialog
  export_data_view.py     — ExportData (currently commented out in main.py)

ViewModel/
  config.py           — (minimal, not fully explored)
```

## Data Flow
1. User loads file in ImportData -> DataManager.set_data(df) -> data_loaded signal emitted
2. All tabs connect to data_loaded: ExploreData, TransformationDataWindow, NetworkVisualizationMod
3. ExploreData: user picks column + operation -> creates a new QWidget+QTableWidget per call, adds to QStackedLayout
4. NetworkVisualizationMod: "Visualizar Red" button -> Worker(QThread) builds graph + layout -> PlotWorker(QThread) builds pg.GraphItem -> emitted to main thread

## Key Design Patterns
- Single shared DataManager instance passed by reference to all tabs
- QThread subclassing (Worker, PlotWorker) for graph layout and rendering preparation
- QStackedLayout used (not QStackedWidget) in ExploreData — new widgets added every operation call
- pyqtgraph PlotWidget for bar charts (explore) and GraphItem for network viz

## Known Structural Issues
- ExploreData.py has unresolved git merge conflict markers still in the file
- Two DataManager files (data_manager.py vs DataManager.py), both imported in different places
- LLM chatbot called synchronously on main thread (chatbot.answer() blocks)
- get_data() in explore_data_view.py instantiates a new exploreData() object on every single call
- No placeholder/loading state shown anywhere in the UI
