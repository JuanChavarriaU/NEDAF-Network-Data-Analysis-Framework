# NEDAF Implementation Plan
## From Pain Points to World-Class Tool

This plan is ordered by dependency — each phase builds on the previous one.
Estimated effort per task uses T-shirt sizes: **S** (<1h), **M** (1-3h), **L** (3-8h), **XL** (1-2 days).

---

## Phase 1: Make It Installable (Week 1)

**Goal**: A new user can `git clone`, `pip install -e .`, and run `nedaf` without issues.

### 1.1 Fix the Basics

| # | Task | Size | Details |
|---|------|------|---------|
| 1.1.1 | Rename `requeriments.txt` → `requirements.txt` | S | Fix typo in filename |
| 1.1.2 | Add `LICENSE` file (MIT) | S | Currently says "Thinking about one" |
| 1.1.3 | Delete empty file `ViewModel/pruebaThreads.py` | S | 0 lines, no purpose |
| 1.1.4 | Remove dead import `graph_tool` from `NetworkAnalysis.py:3` | S | Imported but never used |
| 1.1.5 | Remove unused `import time as tm` from `LLMInsights.py:2` | S | Imported but never used |

### 1.2 Create Package Structure

| # | Task | Size | Details |
|---|------|------|---------|
| 1.2.1 | Create `pyproject.toml` with core dependencies only | M | See spec below |
| 1.2.2 | Create minimal `requirements.txt` (core only, ~10 packages) | S | PyQt6, networkx, pandas, matplotlib, numpy, scipy, pyqtgraph |
| 1.2.3 | Create `requirements-llm.txt` (langchain, openai, chromadb, dotenv) | S | Optional LLM deps |
| 1.2.4 | Create `requirements-gpu.txt` (CUDA/RAPIDS packages) | S | Optional GPU deps |
| 1.2.5 | Create `requirements-dev.txt` (pytest, black, ruff, mypy) | S | Dev tooling |

**pyproject.toml spec:**
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "nedaf"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "PyQt6>=6.6.0",
    "networkx>=3.2.0",
    "pandas>=2.2.0",
    "matplotlib>=3.8.0",
    "numpy>=1.26.0",
    "scipy>=1.13.0",
    "pyqtgraph>=0.13.0",
    "fa2-modified>=0.3.0",
]

[project.optional-dependencies]
llm = ["langchain>=0.2.0", "langchain-openai>=0.1.0", "langchain-community>=0.2.0", "chromadb>=0.5.0", "python-dotenv>=1.0.0"]
ssh = ["paramiko>=3.4.0"]
gpu = ["cudf-cu12>=24.4.0", "cugraph-cu12>=24.4.0"]
dev = ["pytest>=7.0", "black>=24.0", "ruff>=0.4.0", "mypy>=1.0"]

[project.scripts]
nedaf = "main:main"
```

### 1.3 Fix Hard-Coded Paths

| # | Task | Size | Details |
|---|------|------|---------|
| 1.3.1 | Rewrite `ViewModel/config.py` to use env vars + sensible defaults | M | Use `os.getenv()` with `Path` relative to project root |
| 1.3.2 | Add `.env.example` documenting all expected env vars | S | `OPENAI_API_KEY`, `NEDAF_VECTOR_STORE`, `NEDAF_BOOKS_DIR` |

**New `config.py`:**
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

PERSIST_DIR = Path(os.getenv("NEDAF_VECTOR_STORE", BASE_DIR / ".cache" / "vectorstore"))
LOGS_FILE = Path(os.getenv("NEDAF_LOGS", BASE_DIR / "logs" / "nedaf.log"))
FILE_DIR = Path(os.getenv("NEDAF_BOOKS_DIR", BASE_DIR / "data" / "books"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

K = int(os.getenv("NEDAF_LLM_CHUNKS", "4"))

PROMPT_TEMPLATE = """You are a personal Bot assistant for answering any questions about
graph theory, mobility networks, network science, biology and statistics.
..."""
```

### 1.4 Fix Runtime Bugs

| # | Task | Size | Details |
|---|------|------|---------|
| 1.4.1 | Fix `clusterLogin.py:56` — `ImportData()` called without `data_manager` arg | S | Will crash with `TypeError` at runtime |
| 1.4.2 | Fix `Model/ExportData.py` — `setLayout` never called in `initUI` | S | UI layout never applied |
| 1.4.3 | Fix `chatbot.py` — module-level side effects on import (OpenAI connection) | M | Wrap in lazy initialization function |
| 1.4.4 | Fix `retriever.py` — loads all PDFs at import time | M | Wrap in function, call explicitly |

**Phase 1 Deliverable:** `pip install -e .` works. `python main.py` launches without import crashes.

---

## Phase 2: Resolve File Conflicts & Naming (Week 1-2)

**Goal**: The repo can be cloned and used on macOS/Windows without file conflicts.

### 2.1 Resolve Case-Sensitivity File Conflicts

This requires careful git operations since renaming files by case is tricky.

| # | Task | Size | Details |
|---|------|------|---------|
| 2.1.1 | Rename `Model/transformationData.py` → `Model/transformation_logic.py` | S | Pure data logic class |
| 2.1.2 | Rename `Model/TransformationData.py` → `Model/TransformationDataWindow.py` | S | UI widget — will move in Phase 3 |
| 2.1.3 | Rename `ViewModel/exploreData.py` → `ViewModel/explore_logic.py` | S | Pure data logic class |
| 2.1.4 | Rename `ViewModel/ExploreData.py` → `ViewModel/ExploreDataWindow.py` | S | UI widget — will move in Phase 3 |
| 2.1.5 | Update all imports across the project to match new names | M | ~8 files affected |

### 2.2 Standardize Naming Conventions

| # | Task | Size | Details |
|---|------|------|---------|
| 2.2.1 | Rename files to follow Python conventions (`snake_case` for modules) | M | All files in Model/View/ViewModel |
| 2.2.2 | Rename classes to follow PEP 8 (`PascalCase`) | M | `networkStatistics` → `NetworkStatistics`, `exploreData` → `ExploreDataLogic` |
| 2.2.3 | Fix method name `minumumDegree` → `minimumDegree` (typo) | S | In `NetworkAnalysis.py` |

**Full rename map:**
```
Model/
  ImportData.py           → import_data_view.py
  TransformationData.py   → transform_data_view.py
  transformationData.py   → transformation_logic.py
  ExportData.py           → export_data_view.py

View/
  DataManager.py          → data_manager.py
  FileExplorer.py         → file_explorer.py
  clusterLogin.py         → cluster_login.py

ViewModel/
  ExploreData.py          → explore_data_view.py
  exploreData.py          → explore_logic.py
  NetworkVisualizationMod.py → network_visualization.py
  NetworkAnalysis.py      → network_analysis.py
  LLMInsights.py          → llm_insights_view.py
  chatbot.py              → chatbot.py (ok)
  config.py               → config.py (ok)
  retriever.py            → retriever.py (ok)
```

**Phase 2 Deliverable:** Repo clones cleanly on Windows/macOS. Consistent naming.

---

## Phase 3: Fix Architecture (Weeks 2-3)

**Goal**: Proper MVVM separation — each file lives in the right layer.

### 3.1 Understanding the Current Misplacement

```
CURRENTLY IN Model/ (should be in View/):
  - ImportData.py        → QWidget (it's a View)
  - TransformationData.py → QWidget (it's a View)
  - ExportData.py        → QWidget (it's a View)

CURRENTLY IN Model/ (correctly placed):
  - transformationData.py → Pure logic (correct Model)

CURRENTLY IN View/ (should be in ViewModel/):
  - DataManager.py       → State manager with signals (it's a ViewModel)

CURRENTLY IN View/ (correctly placed):
  - FileExplorer.py      → QWidget (correct View)
  - clusterLogin.py      → QDialog (correct View)

CURRENTLY IN ViewModel/ (should be in View/):
  - ExploreData.py       → QWidget (it's a View)
  - LLMInsights.py       → QWidget (it's a View)
  - NetworkVisualizationMod.py → QWidget (it's a View)

CURRENTLY IN ViewModel/ (correctly placed):
  - NetworkAnalysis.py   → Pure logic (correct ViewModel)
  - chatbot.py           → Pure logic (correct ViewModel)
  - config.py            → Configuration (correct ViewModel)
  - retriever.py         → Pure logic (correct ViewModel)

CURRENTLY IN ViewModel/ (should be in Model/):
  - exploreData.py       → Pure data operations (it's a Model)
```

### 3.2 Move Files to Correct Layers

| # | Task | Size | Details |
|---|------|------|---------|
| 3.2.1 | Move `Model/ImportData.py` → `View/import_data_view.py` | S | It's a QWidget |
| 3.2.2 | Move `Model/TransformationData.py` → `View/transform_data_view.py` | S | It's a QWidget |
| 3.2.3 | Move `Model/ExportData.py` → `View/export_data_view.py` | S | It's a QWidget |
| 3.2.4 | Move `Model/transformationData.py` → `Model/transformation_logic.py` | S | Already correct layer, just rename |
| 3.2.5 | Move `View/DataManager.py` → `ViewModel/data_manager.py` | S | It's state management |
| 3.2.6 | Move `ViewModel/ExploreData.py` → `View/explore_data_view.py` | S | It's a QWidget |
| 3.2.7 | Move `ViewModel/LLMInsights.py` → `View/llm_insights_view.py` | S | It's a QWidget |
| 3.2.8 | Move `ViewModel/NetworkVisualizationMod.py` → `View/network_visualization.py` | S | It's a QWidget |
| 3.2.9 | Move `ViewModel/exploreData.py` → `Model/explore_logic.py` | S | Pure data operations |
| 3.2.10 | Update ALL imports in ALL files | L | Every file will need import path updates |
| 3.2.11 | Update `main.py` imports | M | Entry point needs all new paths |

**New structure after Phase 3:**
```
Model/                          # Pure data & logic (NO PyQt)
  ├── __init__.py
  ├── transformation_logic.py   # TransformationData class
  └── explore_logic.py          # exploreData class

View/                           # UI widgets (PyQt6)
  ├── __init__.py
  ├── import_data_view.py       # ImportData widget
  ├── transform_data_view.py    # TransformationDataWindow widget
  ├── export_data_view.py       # ExportData widget (stub)
  ├── explore_data_view.py      # ExploreData widget
  ├── network_visualization.py  # NetworkVisualizationMod widget
  ├── llm_insights_view.py      # LLMInsights widget
  ├── file_explorer.py          # FileExplorer widgets
  └── cluster_login.py          # ClusterLogin dialog

ViewModel/                      # Business logic & state management
  ├── __init__.py
  ├── data_manager.py           # DataManager (central state)
  ├── network_analysis.py       # NetworkAnalysis, NetworkStatistics, NetworkCommunities
  ├── chatbot.py                # LLM chain logic
  ├── retriever.py              # Vector store setup
  └── config.py                 # Configuration
```

**Rule for future contributors:**
- **Model/**: No PyQt imports allowed. Pure Python + pandas/networkx.
- **View/**: QWidget subclasses only. Import from Model/ and ViewModel/.
- **ViewModel/**: Business logic, state management. Can use PyQt signals but NOT QWidgets.

**Phase 3 Deliverable:** Clear separation of concerns. `grep -r "QWidget" Model/` returns nothing.

---

## Phase 4: Code Quality (Weeks 3-4)

**Goal**: Clean, professional code. Debug prints removed. Proper logging.

### 4.1 Remove Debug Code

| # | Task | Size | Details |
|---|------|------|---------|
| 4.1.1 | Remove all 18 `print()` debug statements | S | Replace with logger calls |
| 4.1.2 | Remove all commented-out code blocks | M | TransformationData.py, tests.py, main.py |
| 4.1.3 | Remove `chroma_data/` from repo (add to .gitignore) | S | Generated data shouldn't be tracked |

### 4.2 Add Logging

| # | Task | Size | Details |
|---|------|------|---------|
| 4.2.1 | Create `nedaf/logging_config.py` with rotating file + console handler | M | Use stdlib `logging` |
| 4.2.2 | Replace all `print()` with appropriate log levels | M | DEBUG for dev, INFO for user, ERROR for failures |

### 4.3 Add Thread Safety to DataManager

| # | Task | Size | Details |
|---|------|------|---------|
| 4.3.1 | Add `threading.RLock` to `DataManager.set_data` and `get_data` | M | Currently shared across threads unsafely |
| 4.3.2 | Return `.copy()` from `get_data` to prevent mutation | S | Defensive copy |

### 4.4 Cache Expensive Operations

| # | Task | Size | Details |
|---|------|------|---------|
| 4.4.1 | Cache community detection in `NetworkCommunities` | M | Called 4+ times with same graph, each call is O(n²) |
| 4.4.2 | Add `@staticmethod` decorators to undecorated static methods | S | NetworkStatistics and NetworkCommunities methods |

### 4.5 Fix Error Handling

| # | Task | Size | Details |
|---|------|------|---------|
| 4.5.1 | Fix `DataManager.QMessageBox.critical(self, ...)` — self is QObject not QWidget | S | Will crash if error occurs |
| 4.5.2 | Add input validation in `TransformationData.normalize_data` (div by zero) | S | Crashes when min == max |
| 4.5.3 | Add file size/format validation in `ImportData.LoadData` | M | No limits on file size currently |
| 4.5.4 | Add timeout to SSH connections in `clusterLogin.py` | S | Currently hangs indefinitely |

### 4.6 Fix Memory Leaks

| # | Task | Size | Details |
|---|------|------|---------|
| 4.6.1 | Clean up old tabs in `ExploreData.on_operation_changed` | M | Creates new tab every dropdown change, never removes old ones |
| 4.6.2 | Add `deleteLater()` for replaced widgets | S | PyQt memory management |

**Phase 4 Deliverable:** Zero print statements. Proper logging. Thread-safe state. No crashes on edge cases.

---

## Phase 5: Internationalization (Week 4)

**Goal**: All code in English. UI strings externalized for future i18n.

### 5.1 Code Language Standardization

| # | Task | Size | Details |
|---|------|------|---------|
| 5.1.1 | Rename Spanish variables to English | M | `importar_tab` → `import_tab`, `transformar_tab` → `transform_tab`, etc. |
| 5.1.2 | Translate all Spanish comments to English | M | ~30 comments across codebase |
| 5.1.3 | Move all UI-facing strings to a constants file | L | Create `View/strings.py` with all user-visible text |

**`View/strings.py` example:**
```python
# UI Strings - English (default)
TAB_IMPORT = "Import Data"
TAB_TRANSFORM = "Data Transformation"
TAB_EXPLORE = "Data Exploration"
TAB_VISUALIZE = "Data Visualization"
TAB_LLM = "LLM Insights"

MENU_OPTIONS = "Options"
MENU_CLUSTER = "Cluster Connection"

ERROR_LOAD_FAILED = "An error occurred: {error}"
ERROR_CONNECTION = "Failed to connect: {error}"

PLACEHOLDER_QUERY = "Send a query to NEDAF Assistant"
BUTTON_SEND = "Send"
BUTTON_LOAD = "Load Data"
BUTTON_APPLY = "Apply Transformations"
```

**Phase 5 Deliverable:** All code reads naturally in English. UI strings centralized.

---

## Phase 6: Testing & CI (Weeks 4-5)

**Goal**: 60%+ test coverage. CI blocks broken PRs.

### 6.1 Restructure Tests

| # | Task | Size | Details |
|---|------|------|---------|
| 6.1.1 | Create `tests/` directory structure | S | `tests/unit/`, `tests/integration/`, `tests/fixtures/` |
| 6.1.2 | Move existing tests from `tests.py` → `tests/unit/test_network_analysis.py` | M | Split into 3 files matching 3 test classes |
| 6.1.3 | Uncomment and fix `TestTransformationData` | M | Currently commented out in tests.py |
| 6.1.4 | Uncomment and fix `TestExploreData` | M | Currently commented out in tests.py |
| 6.1.5 | Add `pytest.ini` or `[tool.pytest]` in pyproject.toml | S | Configure test discovery |

### 6.2 Add New Tests

| # | Task | Size | Details |
|---|------|------|---------|
| 6.2.1 | Test `DataManager` set/get/signal cycle | M | Core state management |
| 6.2.2 | Test `ImportData.LoadData` with each format (CSV, Parquet, Excel, MTX, edges) | L | Use sample fixtures |
| 6.2.3 | Test `TransformationData` normalize + cut missing | M | Edge cases: empty df, constant column |
| 6.2.4 | Test `exploreData` statistical functions | M | Against known values |
| 6.2.5 | Test `config.py` env var loading | S | Mock os.getenv |
| 6.2.6 | Create sample fixture files in `tests/fixtures/` | M | Small CSV, MTX, edges files |

### 6.3 Add CI

| # | Task | Size | Details |
|---|------|------|---------|
| 6.3.1 | Create `.github/workflows/tests.yml` | M | Run pytest on push/PR |
| 6.3.2 | Create `.github/workflows/lint.yml` | M | Run ruff + black check |
| 6.3.3 | Add pre-commit config (`.pre-commit-config.yaml`) | M | black, ruff, mypy |
| 6.3.4 | Add branch protection rules (document in CONTRIBUTING.md) | S | Require CI pass before merge |

**Phase 6 Deliverable:** `pytest` runs. CI blocks broken PRs. 60%+ coverage on Model/ and ViewModel/.

---

## Phase 7: Documentation (Week 5-6)

**Goal**: A new contributor can understand, install, and contribute within 30 minutes.

### 7.1 Core Documentation

| # | Task | Size | Details |
|---|------|------|---------|
| 7.1.1 | Rewrite `README.md` with badges, screenshots, quick start | L | See template in PAIN_POINTS_ANALYSIS.md |
| 7.1.2 | Create `CONTRIBUTING.md` (setup, PR process, code style) | M | Include branch naming, commit conventions |
| 7.1.3 | Create `CODE_OF_CONDUCT.md` | S | Use Contributor Covenant template |
| 7.1.4 | Create `CHANGELOG.md` | S | Start with v0.1.0 |
| 7.1.5 | Create `docs/ARCHITECTURE.md` with layer rules | M | Explain MVVM, what goes where |

### 7.2 Code Documentation

| # | Task | Size | Details |
|---|------|------|---------|
| 7.2.1 | Add docstrings to all public classes | L | One-line summary + params |
| 7.2.2 | Add type hints to all public methods | L | Use `pd.DataFrame`, `nx.Graph`, etc. |

### 7.3 Community Infrastructure

| # | Task | Size | Details |
|---|------|------|---------|
| 7.3.1 | Create GitHub issue templates (bug, feature, question) | M | `.github/ISSUE_TEMPLATE/` |
| 7.3.2 | Create PR template | S | `.github/PULL_REQUEST_TEMPLATE.md` |
| 7.3.3 | Add "good first issue" labels to easy tasks | S | Tag ~10 issues |
| 7.3.4 | Enable GitHub Discussions | S | Q&A, Ideas, Show and Tell |

**Phase 7 Deliverable:** README has quick start. CONTRIBUTING.md exists. Architecture documented.

---

## Phase 8: UX & Features (Weeks 6-8)

**Goal**: Professional polish. CLI support. Better LLM integration.

### 8.1 CLI Support

| # | Task | Size | Details |
|---|------|------|---------|
| 8.1.1 | Add `click` dependency | S | Lightweight CLI framework |
| 8.1.2 | Create `cli.py` with `gui`, `analyze`, `communities` subcommands | L | See spec in PAIN_POINTS_ANALYSIS.md |
| 8.1.3 | Update `pyproject.toml` entry point to support both GUI and CLI | S | `nedaf gui` and `nedaf analyze` |

### 8.2 LLM Integration Improvements

| # | Task | Size | Details |
|---|------|------|---------|
| 8.2.1 | Make LLM features gracefully degrade when no API key | M | Show "Configure API key" message instead of crash |
| 8.2.2 | Run LLM queries in background thread | M | Currently blocks UI during inference |
| 8.2.3 | Add loading spinner during LLM responses | S | Better UX feedback |

### 8.3 UI Polish

| # | Task | Size | Details |
|---|------|------|---------|
| 8.3.1 | Add progress bars for file loading | M | Large files block UI |
| 8.3.2 | Add status bar messages | S | Show current operation |
| 8.3.3 | Complete ExportData implementation | L | Currently a stub (12 lines) |

**Phase 8 Deliverable:** CLI works. LLM doesn't crash without API key. Export works.

---

## Execution Summary

### Timeline at a Glance

```
Week 1:   Phase 1 (Installable) + Phase 2 (File Conflicts)
Week 2:   Phase 2 (finish) + Phase 3 (Architecture)
Week 3:   Phase 3 (finish) + Phase 4 (Code Quality)
Week 4:   Phase 4 (finish) + Phase 5 (i18n) + Phase 6 (Testing start)
Week 5:   Phase 6 (Testing finish) + Phase 7 (Documentation)
Week 6-8: Phase 7 (finish) + Phase 8 (UX & Features)
```

### Task Count by Phase

| Phase | Tasks | Estimated Hours |
|-------|-------|----------------|
| 1. Installable | 16 | 8-12h |
| 2. File Conflicts | 8 | 4-6h |
| 3. Architecture | 11 | 8-12h |
| 4. Code Quality | 12 | 10-14h |
| 5. i18n | 3 | 4-6h |
| 6. Testing & CI | 10 | 12-16h |
| 7. Documentation | 9 | 10-14h |
| 8. UX & Features | 9 | 14-18h |
| **Total** | **78 tasks** | **70-98h** |

### Open-Source Readiness Checklist

Before announcing publicly:

- [ ] **Phase 1 complete** — `pip install` works
- [ ] **Phase 2 complete** — clones on all OS
- [ ] **Phase 3 complete** — architecture makes sense
- [ ] **Phase 4 complete** — no debug prints, proper logging
- [ ] **Phase 5 complete** — all code in English
- [ ] **Phase 6 complete** — CI passes, tests exist
- [ ] **Phase 7 complete** — README, CONTRIBUTING, LICENSE exist
- [ ] `LICENSE` file added (MIT recommended)
- [ ] No secrets/API keys in code or git history
- [ ] No hard-coded paths remaining
- [ ] GitHub repo description and topics set
- [ ] At least 5 "good first issue" items tagged

### Quick Wins (Can Do Right Now in <1h)

1. Rename `requeriments.txt` → `requirements.txt`
2. Add `LICENSE` (MIT)
3. Delete `ViewModel/pruebaThreads.py`
4. Remove `import graph_tool.all as gt` from `NetworkAnalysis.py`
5. Remove `import time as tm` from `LLMInsights.py`
6. Fix `ExportData.initUI` — add `self.setLayout(layout)`
7. Fix typo `minumumDegree` → `minimumDegree`
