import polars as pl

# Global state to hold the dataset since it's a local application
# In a production environment, this would be handled via a database, Redis, or session management.
class AppState:
    def __init__(self):
        self._data: pl.DataFrame | None = None
        self._graph_metrics: dict | None = None

    def set_data(self, data: pl.DataFrame):
        self._data = data

    def get_data(self) -> pl.DataFrame | None:
        return self._data
        
    def set_graph_metrics(self, metrics: dict):
        self._graph_metrics = metrics
        
    def get_graph_metrics(self) -> dict | None:
        return self._graph_metrics

app_state = AppState()
