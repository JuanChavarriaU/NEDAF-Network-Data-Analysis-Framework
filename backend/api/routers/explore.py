from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import polars as pl
from api.state import app_state
from Model.explore_logic import exploreData
import polars.selectors as cs

router = APIRouter()


from typing import Optional  # noqa: E402


class ColumnRequest(BaseModel):
    column: str
    sample_size: Optional[int] = None


def get_explore_data() -> exploreData:
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    explore = exploreData()
    explore.set_data(data)
    return explore


@router.get("/numeric-columns")
def get_numeric_columns():
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    return {"columns": data.select(cs.numeric()).columns}


@router.get("/columns-info")
def get_columns_info():
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")

    info = []
    numeric_cols = set(data.select(cs.numeric()).columns)
    for col in data.columns:
        col_type = "numeric" if col in numeric_cols else "categorical"
        info.append({"name": col, "type": col_type})

    return {"columns": info}


@router.post("/summary")
def get_summary(req: ColumnRequest):
    exp = get_explore_data()
    try:
        df = exp.get_summary_statistics(req.column)
        return df.to_dicts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/distribution")
def get_distribution(req: ColumnRequest):
    exp = get_explore_data()
    try:
        df = exp.calculate_distribution(req.column, sample_size=req.sample_size)
        return df.to_dicts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/correlation")
def get_correlation(req: ColumnRequest):
    exp = get_explore_data()
    try:
        df = exp.calculate_correlation(req.column)
        return {"columns": df.columns, "data": df.to_dicts()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/covariance")
def get_covariance():
    exp = get_explore_data()
    try:
        df = exp.calculate_covariance()
        return {"columns": df.columns, "data": df.to_dicts()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics")
def get_single_metrics(req: ColumnRequest):
    exp = get_explore_data()
    try:
        data = app_state.get_data()
        is_num = data[req.column].dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32]

        metrics = {
            "unique_values": exp.get_unique_values(req.column),
            "missing_values": exp.get_missing_values(req.column),
        }

        if is_num:
            min_max_df = exp.calculate_min_max(req.column)
            metrics.update(
                {
                    "mean": exp.calculate_mean(req.column),
                    "median": exp.calculate_median(req.column),
                    "variance": exp.calculate_variance(req.column),
                    "std_dev": exp.calculate_standard_deviation(req.column),
                    "min_max": [min_max_df["Valor"][0], min_max_df["Valor"][1]],
                }
            )

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
