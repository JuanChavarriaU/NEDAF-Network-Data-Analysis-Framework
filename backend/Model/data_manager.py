"""
DataManager - Central state management for NEDAF.

Provides thread-safe access to shared DataFrame across the application.
"""
import polars as pl
import logging
from threading import RLock
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger("nedaf.data_manager")


class DataManager(QObject):
    """Thread-safe data manager for the application."""

    data_loaded = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._data = None
        self._lock = RLock()

    def set_data(self, data: pl.DataFrame):
        """
        Set the DataFrame in the manager (thread-safe).

        Args:
            data: DataFrame to store

        Raises:
            ValueError: If data is None or invalid type
        """
        if data is None:
            raise ValueError("Cannot set None as data")

        with self._lock:
            self._data = data
            logger.info(f"Data loaded: {len(data)} rows, {len(data.columns)} columns")
            self.data_loaded.emit()

    def get_data(self):
        """
        Get a copy of the DataFrame (thread-safe).

        Returns:
            Copy of the stored DataFrame, or None if no data loaded
        """
        with self._lock:
            if self._data is None:
                logger.warning("get_data() called but no data loaded")
                return None
            # Return a copy to prevent external mutation
            if hasattr(self._data, 'clone'):
                return self._data.clone()
            return self._data.copy()

    def has_data(self) -> bool:
        """Check if data is loaded."""
        with self._lock:
            return self._data is not None



