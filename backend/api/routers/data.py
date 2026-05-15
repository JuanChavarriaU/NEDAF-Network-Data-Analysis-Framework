from fastapi import APIRouter, HTTPException, UploadFile, File
import tempfile
import os
import polars as pl
import networkx as nx
from scipy.io import mmread
from scipy.sparse import csr_matrix
from api.state import app_state
from Model.transformation_logic import TransformationData

router = APIRouter()


MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
VALID_EXTENSIONS = {".csv", ".parquet", ".gml", ".mtx"}


@router.post("/load")
async def load_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in VALID_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Please provide a file ending in one of: {', '.join(VALID_EXTENSIONS)}"
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            file_size = 0
            while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    os.remove(tmp.name)
                    raise HTTPException(status_code=413, detail="File too large. Limit is 500MB.")
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            if ext == ".csv":
                data = pl.read_csv(tmp_path)
            elif ext == ".parquet":
                data = pl.read_parquet(tmp_path)
            elif ext == ".gml":
                graph = nx.read_gml(tmp_path)
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
            elif ext == ".mtx":
                mat = mmread(tmp_path)
                if not isinstance(mat, csr_matrix):
                    mat = mat.tocsr()
                sources, targets = mat.nonzero()
                weights = mat.data
                data = pl.DataFrame({"source": sources, "target": targets, "weight": weights})
            else:
                # Should not reach here due to earlier validation, but keeping for safety
                raise HTTPException(status_code=400, detail="Invalid extension.")

            app_state.set_data(data)

            return {"message": "File loaded successfully", "columns": data.columns, "rows": len(data)}
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Error reading file. The file may be corrupted, malformed, or of an incorrect type.")


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
