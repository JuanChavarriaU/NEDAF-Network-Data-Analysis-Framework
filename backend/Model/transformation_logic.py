"""
Data transformation logic for NEDAF.

Provides operations to clean and normalize network data.
"""

import polars as pl
import logging

logger = logging.getLogger("nedaf.transformation_logic")


class TransformationData:
    """Handles data transformation operations on network DataFrames."""

    def __init__(self, dataframe: pl.DataFrame):
        """
        Initialize with a DataFrame containing network data.

        Args:
            dataframe: DataFrame with network data (typically with columns like
                      'source', 'destination', and optionally 'weight')

        Raises:
            ValueError: If dataframe is None or empty
        """
        super().__init__()

        if dataframe is None or len(dataframe) == 0:
            raise ValueError("DataFrame cannot be None or empty")

        self.dataframe = dataframe
        logger.debug(f"TransformationData initialized with {len(dataframe)} rows")

    def cut_missing_values(self):
        """
        Remove rows with missing values.

        Returns:
            Self for method chaining
        """
        original_len = len(self.dataframe)

        if isinstance(self.dataframe, pl.DataFrame):
            self.dataframe = self.dataframe.drop_nulls()
        else:
            self.dataframe = self.dataframe.dropna()

        removed = original_len - len(self.dataframe)

        if removed > 0:
            logger.info(f"Removed {removed} rows with missing values")

        return self

    def normalize_data(self):
        """
        Normalize values in the weight column to [0, 1] range.

        The weight column is assumed to be the third column (index 2).
        Creates a new 'normalized_weight' column.

        Raises:
            ValueError: If weight column has constant values (min == max)
            IndexError: If DataFrame has fewer than 3 columns

        Returns:
            Self for method chaining
        """
        if len(self.dataframe.columns) < 3:
            raise IndexError("DataFrame must have at least 3 columns for normalization")

        weight_col = self.dataframe.columns[2]

        if isinstance(self.dataframe, pl.DataFrame):
            min_val = self.dataframe.select(pl.col(weight_col).min()).item()
            max_val = self.dataframe.select(pl.col(weight_col).max()).item()

            if min_val == max_val:
                logger.warning(
                    f"Column '{weight_col}' has constant value {min_val}, cannot normalize"
                )
                raise ValueError(
                    f"Cannot normalize column '{weight_col}' - all values are {min_val}"
                )

            self.dataframe = self.dataframe.with_columns(
                ((pl.col(weight_col) - min_val) / (max_val - min_val)).alias("normalized_weight")
            )
        else:
            min_val = self.dataframe[weight_col].min()
            max_val = self.dataframe[weight_col].max()

            if min_val == max_val:
                logger.warning(
                    f"Column '{weight_col}' has constant value {min_val}, cannot normalize"
                )
                raise ValueError(
                    f"Cannot normalize column '{weight_col}' - all values are {min_val}"
                )

            self.dataframe["normalized_weight"] = (self.dataframe[weight_col] - min_val) / (
                max_val - min_val
            )

        logger.info(f"Normalized column '{weight_col}' from [{min_val}, {max_val}] to [0, 1]")
        return self

    def get_data(self) -> pl.DataFrame:
        """
        Get the transformed DataFrame.

        Returns:
            The DataFrame with all applied transformations
        """
        return self.dataframe
