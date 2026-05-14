from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import polars as pl
import networkx as nx
from scipy.io import mmread
from scipy.sparse import csr_matrix
from api.state import app_state
from Model.transformation_logic import TransformationData

router = APIRouter()


class LoadFileRequest(BaseModel):
    file_path: str


@router.post("/load")
def load_file(request: LoadFileRequest):
    file_path = request.file_path.strip()
    file_path_lower = file_path.lower()
    try:
        if file_path_lower.endswith(".csv"):
            data = pl.read_csv(file_path)
        elif file_path_lower.endswith(".parquet"):
            data = pl.read_parquet(file_path)
        elif file_path_lower.endswith(".gml"):
            graph = nx.read_gml(file_path)
            edges = list(graph.edges(data=True))
            if edges and len(edges[0]) == 3 and edges[0][2]:
                data = pl.DataFrame(
                    [
                        {"source": u, "target": v, "weight": d.get("weight", 1.0)}
                        for u, v, d in edges
                    ]
                )
            else:
                data = pl.DataFrame([{"source": u, "target": v} for u, v, d in edges])
        elif file_path_lower.endswith(".mtx"):
            mat = mmread(file_path)
            if not isinstance(mat, csr_matrix):
                mat = mat.tocsr()
            sources, targets = mat.nonzero()
            weights = mat.data
            data = pl.DataFrame({"source": sources, "target": targets, "weight": weights})
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please provide a path ending in .csv, .parquet, .gml, or .mtx",
            )

        app_state.set_data(data)

        return {"message": "File loaded successfully", "columns": data.columns, "rows": len(data)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.get("/columns")
def get_columns():
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    return {"columns": data.columns}


@router.post("/transform/drop-nulls")
def drop_nulls():
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")

    transform = TransformationData(data)
    transform.drop_nulls()
    new_data = transform.get_data()
    app_state.set_data(new_data)

    return {"message": "Nulls dropped", "rows": len(new_data)}


@router.post("/transform/normalize")
def normalize():
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")

    try:
        transform = TransformationData(data)
        transform.normalize_data()
        new_data = transform.get_data()
        app_state.set_data(new_data)
        return {"message": "Data normalized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
