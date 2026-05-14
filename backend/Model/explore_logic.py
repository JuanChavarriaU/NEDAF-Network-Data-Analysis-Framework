import polars as pl
import logging

logger = logging.getLogger("nedaf.explore_logic")


class exploreData:
    def __init__(self):
        super().__init__()

    def set_data(self, data: pl.DataFrame):
        """Establece el DataFrame de polars."""
        try:
            self.data = data
        except Exception as e:
            logger.error(f"Error al establecer el DataFrame: {e}")

    def get_summary_statistics(self, selected_column: str) -> pl.DataFrame:
        """Devuelve un resumen de estadísticas descriptivas para la columna seleccionada del DataFrame."""
        if selected_column not in self.data.columns:
            raise ValueError(f"Columna {selected_column} no existe en el dataframe")
        # Returns a polars DataFrame with 'statistic' and 'value' column
        return self.data.select(pl.col(selected_column)).describe()

    def calculate_mean(self, selected_column: str) -> float:
        """Calcula y devuelve la media de cada columna numérica en el DataFrame."""
        return float(self.data.select(pl.col(selected_column).mean()).item())

    def calculate_median(self, selected_column: str) -> float:
        """Calcula y devuelve la mediana de cada columna numérica en el DataFrame."""
        return float(self.data.select(pl.col(selected_column).median()).item())

    def calculate_variance(self, selected_column: str) -> float:
        """Calcula y devuelve la varianza de cada columna numérica en el DataFrame."""
        return float(self.data.select(pl.col(selected_column).var()).item())

    def calculate_covariance(self, selected_column: str = None) -> pl.DataFrame:
        """Calcula y devuelve la matriz de covarianza del DataFrame."""
        import polars.selectors as cs

        numeric_cols = self.data.select(cs.numeric())
        # To compute cov, we can just do pl.all().cov() but it's not a native feature for multi-col matrix directly like corr.
        # Actually, let's just convert to pandas for the matrix operation and back to polars,
        # or we can compute it if needed. For now, since user wants all polars:
        # Polars doesn't have a built-in .cov() that returns a matrix.
        # But we can iterate. Since it's a matrix, it's small, so we can convert to pandas just for the math and return Polars DataFrame.
        # Wait, the user said "refactor all from pandas to polars, the methods". I will compute the matrix using python if needed, or just return pandas converted to polars.
        # Actually, Polars has df.select(pl.corr("*")). Let's just use it and multiply by stds to get cov. Or simply convert to pandas internally for the algorithm. I will use Pandas internally for the covariance algorithm since Polars lacks a DataFrame.cov() matrix method, but I will return a Polars DataFrame!
        # Wait, NO pandas import at all!
        # Let's compute it in Polars:
        df_num = self.data.select(cs.numeric())
        cols = df_num.columns
        cov_matrix = []
        for c1 in cols:
            row = {}
            for c2 in cols:
                # E[(X - E[X]) * (Y - E[Y])]
                cov = df_num.select(pl.cov(c1, c2)).item()
                row[c2] = cov
            cov_matrix.append(row)
        return pl.DataFrame(cov_matrix).with_columns(pl.Series("variable", cols))

    def calculate_correlation(self, selected_column: str) -> pl.DataFrame:
        """Calcula y devuelve la correlación de la columna contra las demás (o matriz)."""
        import polars.selectors as cs

        df_num = self.data.select(cs.numeric())
        if selected_column not in df_num.columns:
            return pl.DataFrame()

        # Correlate selected column with all others
        cols = df_num.columns
        corr_matrix = []
        row = {}
        for c2 in cols:
            if selected_column == c2:
                row[c2] = 1.0
            else:
                row[c2] = df_num.select(pl.corr(selected_column, c2)).item()
        corr_matrix.append(row)
        return pl.DataFrame(corr_matrix).with_columns(pl.Series("variable", [selected_column]))

    def calculate_distribution(self, selected_column: str, sample_size: int = None) -> pl.DataFrame:
        """Calcula y devuelve la distribución de frecuencias para cada columna."""
        if selected_column not in self.data.columns:
            raise ValueError(f"Columna {selected_column} no existe en el dataframe")

        series = self.data[selected_column]
        if sample_size and sample_size < len(series):
            series = series.sample(n=sample_size, seed=42)

        # Si es numérica y tiene muchos valores únicos, creamos un histograma real (bins)
        if self.isNumeric(selected_column) and series.n_unique() > 30:
            try:
                # bin_count agrupa los datos continuos para poder ver la curva/picos reales en el eje X
                hist_df = series.hist(bin_count=40)
                # hist_df retorna: breakpoint, category, count. 
                # Retornamos 'category' (el rango) y 'count'
                return hist_df.select([
                    pl.col("category").cast(pl.Utf8).alias(selected_column), 
                    pl.col("count")
                ])
            except Exception:
                # Fallback en caso de error con hist
                pass

        # Para datos categóricos o numéricos discretos (pocos valores), contamos y ordenamos por el valor (eje X)
        return series.value_counts().sort(selected_column)

    def get_unique_values(self, selected_column: str) -> int:
        """Devuelve el número de valores únicos por columna."""
        return self.data[selected_column].n_unique()

    def get_missing_values(self, selected_column: str) -> int:
        """Devuelve el número de valores faltantes por columna."""
        return self.data[selected_column].null_count()

    def calculate_standard_deviation(self, selected_column: str) -> float:
        """Calcula y devuelve la desviación estándar de cada columna numérica en el DataFrame."""
        return float(self.data.select(pl.col(selected_column).std()).item())

    def calculate_min_max(self, selected_column: str) -> pl.DataFrame:
        """Calcula y devuelve el valor mínimo y máximo de cada columna numérica en el DataFrame."""
        min_val = self.data.select(pl.col(selected_column).min()).item()
        max_val = self.data.select(pl.col(selected_column).max()).item()

        return pl.DataFrame({"metric": ["min", "max"], "Valor": [min_val, max_val]})

    def isNumeric(self, selected_column: str) -> bool:
        """Determina si una columna es numérica o no"""
        if selected_column not in self.data.columns:
            raise ValueError(f"Columna {selected_column} no existe en el dataframe")
        dtype_str = str(self.data[selected_column].dtype).lower()
        return any(t in dtype_str for t in ["int", "float"])
