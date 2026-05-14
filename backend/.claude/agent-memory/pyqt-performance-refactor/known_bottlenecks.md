---
name: NEDAF Known Bottlenecks and Pain Points
description: Concrete performance and UX issues identified by code review, with file:line references
type: project
---

# Top Bottlenecks (ranked by impact)

## 1. LLM chatbot blocks the UI thread
- File: View/llm_insights_view.py:44 — `response = chatbot.answer(query)` called directly in `on_send_clicked`
- chatbot.answer() makes a synchronous OpenAI network call; the entire Qt event loop freezes
- Fix: QThread or QThreadPool worker with a signal to deliver the response

## 2. QStackedLayout widget leak — new widget created on every operation change
- File: View/explore_data_view.py:57-70 — create_tab() creates a new QWidget+QTableWidget and adds it to the stack EVERY TIME
- on_operation_changed fires every dropdown change; after 10 selections there are 10 orphaned widgets in the stack
- Fix: pre-create one reusable QTableWidget per operation slot, or clear and reuse a single table

## 3. get_data() instantiates a new exploreData() object on every call
- File: View/explore_data_view.py:209-218 — called multiple times per operation (once in on_column_changed, then again in fill_table_*)
- Each call wraps the same DataFrame in a new object; wastes allocation and is confusing
- Fix: cache exploreData as self._explore_data, invalidate on data_loaded

## 4. NetworkAnalysis metrics computed synchronously on main thread
- File: View/network_visualization.py:161-177 — on_operation_changed() calls expensive nx functions (betweenness centrality, diameter, avg path length) directly on the main thread
- networkDiameter and networkAveragePathLength are O(VE) — will freeze UI for seconds on real graphs
- Worker thread exists for layout but not for metric computation

## 5. PlotWorker constructs node adjacency index with O(N*E) list search
- File: View/network_visualization.py:234 — `nodes.index(source)` inside a list comprehension over all edges
- nodes.index() is O(N) linear scan; for a graph with 1000 nodes and 5000 edges = 5M iterations
- Fix: build a dict {node: idx} once before the loop

## 6. useCache=False on GraphItem disables pyqtgraph's render cache
- File: View/network_visualization.py:244 — `useCache=False` passed to pg.GraphItem
- Disables the internal item cache, forcing full redraw on every frame
- Fix: remove or set to True (default)

## 7. ExploreData.py has live merge conflict markers
- File: View/ExploreData.py:3-10 — unresolved <<<<<<< HEAD / ======= / >>>>>>> markers in source
- This file will fail to import; it's the old version but is still present on disk
- The working version is explore_data_view.py

## 8. Duplicate DataManager imports cause silent runtime confusion
- View/transform_data_view.py imports BOTH `from Model.transformation_logic import TransformationData` and `from Model.DataManager import DataManager` (duplicate import lines 7 and 10)
- Two DataManager files exist (data_manager.py and DataManager.py) with identical content; different modules import different ones, making the shared state non-obvious

## 9. Table fill loops use pandas .loc indexing inside nested Python loops
- File: View/explore_data_view.py:278-281 — `correlation.loc[index, column]` inside double for-loop
- .loc label lookup in a loop is slower than iterating over .values directly
- Fix: iterate over correlation.values with enumerate

## 10. add_and_show_widget() double-adds widgets to QStackedLayout
- File: View/explore_data_view.py:174-176 — create_tab() already calls stacked_Layout.addWidget(tab) on line 66, then add_and_show_widget() calls it again on line 175
- This adds the same widget twice to the stack, corrupting the index

## 11. is_numeric() uses invalid Python union syntax as isinstance argument
- File: View/explore_data_view.py:402 — `isinstance(value, (float|int, float|int))` is invalid; float|int is a union type, not a tuple of types
- Should be `isinstance(value, (int, float))`
