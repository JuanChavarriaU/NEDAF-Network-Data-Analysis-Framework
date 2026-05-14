from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from api.state import app_state
from Model.NetworkAnalysis import NetworkAnalysis, networkStatistics, NetworkCommunities
import polars as pl
import logging

logger = logging.getLogger("nedaf.graph")

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers – pure Polars, no NetworkX needed at this layer
# ---------------------------------------------------------------------------


def _compute_degree_df(data: pl.DataFrame) -> pl.DataFrame:
    """Return a DataFrame with columns [node, degree] for the full edge list."""
    cols = data.columns
    src_col, dst_col = cols[0], cols[1]
    src_deg = data.group_by(src_col).agg(pl.len().alias("deg")).rename({src_col: "node"})
    tgt_deg = data.group_by(dst_col).agg(pl.len().alias("deg")).rename({dst_col: "node"})
    return pl.concat([src_deg, tgt_deg]).group_by("node").agg(pl.sum("deg").alias("degree"))


def _sample_random(data: pl.DataFrame, n_edges: int, seed: int) -> pl.DataFrame:
    """Pure random edge sampling – O(n log n) in Polars, extremely fast."""
    n = min(n_edges, len(data))
    return data.sample(n=n, seed=seed, shuffle=True)


def _sample_degree_weighted(data: pl.DataFrame, n_edges: int, seed: int) -> pl.DataFrame:
    """
    Induced subgraph of the top-K highest-degree nodes.
    Hub-preserving: ensures the most connected nodes always appear in the sample.
    """
    cols = data.columns
    src_col, dst_col = cols[0], cols[1]
    degree_df = _compute_degree_df(data)

    # Binary-search the top-K nodes that yield ~n_edges edges
    # Start with a rough estimate: avg degree ≈ 2*n_edges/K → K ≈ 2*n_edges/avg_deg
    avg_deg = degree_df["degree"].mean() or 1.0
    k = max(10, int(2 * n_edges / avg_deg))

    for _ in range(8):  # at most 8 iterations to converge
        top_nodes = degree_df.sort("degree", descending=True).head(k)["node"]
        induced = data.filter(pl.col(src_col).is_in(top_nodes) & pl.col(dst_col).is_in(top_nodes))
        n_induced = len(induced)
        if n_induced >= n_edges or k >= len(degree_df):
            break
        k = min(int(k * 1.5), len(degree_df))

    # Trim to exactly n_edges if over
    if len(induced) > n_edges:
        induced = induced.sample(n=n_edges, seed=seed, shuffle=True)
    return induced


def _sample_snowball(data: pl.DataFrame, n_edges: int, seed: int) -> pl.DataFrame:
    """
    Snowball sampling starting from the highest-degree node.
    Traverses the neighbourhood BFS-style until n_edges is reached.
    Structure-preserving: produces a connected subgraph.
    """
    import random

    rng = random.Random(seed)

    cols = data.columns
    src_col, dst_col = cols[0], cols[1]

    degree_df = _compute_degree_df(data)
    # Seed node = highest degree
    seed_node = degree_df.sort("degree", descending=True).head(1)["node"][0]

    visited_nodes: set[str] = {seed_node}
    frontier: list[str] = [seed_node]
    collected_edges: list[tuple] = []

    # Build an adjacency index in Polars for fast lookups
    # group edges by source for O(1) neighbour retrieval
    adj_src = (
        data.group_by(src_col).agg(
            pl.struct([dst_col, cols[2]] if len(cols) >= 3 else [dst_col]).alias("neighbors")
        )
    ).to_dict(as_series=False)

    adj_tgt = (
        data.group_by(dst_col).agg(
            pl.struct([src_col, cols[2]] if len(cols) >= 3 else [src_col]).alias("neighbors")
        )
    ).to_dict(as_series=False)

    # Build Python dicts for fast BFS
    src_to_neighbors: dict[str, list] = {}
    for node, nbrs in zip(adj_src[src_col], adj_src["neighbors"]):
        src_to_neighbors[node] = nbrs

    tgt_to_neighbors: dict[str, list] = {}
    for node, nbrs in zip(adj_tgt[dst_col], adj_tgt["neighbors"]):
        tgt_to_neighbors[node] = nbrs

    weight_col = cols[2] if len(cols) >= 3 else None

    while frontier and len(collected_edges) < n_edges:
        rng.shuffle(frontier)
        next_frontier: list[str] = []

        for node in frontier:
            if len(collected_edges) >= n_edges:
                break

            neighbors_out = src_to_neighbors.get(node, [])
            neighbors_in = tgt_to_neighbors.get(node, [])

            for nbr_struct in neighbors_out + neighbors_in:
                if len(collected_edges) >= n_edges:
                    break
                if weight_col:
                    nbr_node = nbr_struct.get(dst_col) or nbr_struct.get(src_col)
                    w = nbr_struct.get(weight_col, 1.0)
                else:
                    nbr_node = nbr_struct.get(dst_col) or nbr_struct.get(src_col)
                    w = 1.0

                if nbr_node and nbr_node not in visited_nodes:
                    visited_nodes.add(nbr_node)
                    next_frontier.append(nbr_node)
                    edge = (node, nbr_node, w) if weight_col else (node, nbr_node)
                    collected_edges.append(edge)

        frontier = next_frontier

    if weight_col:
        return pl.DataFrame(collected_edges, schema=[src_col, dst_col, weight_col], orient="row")
    else:
        return pl.DataFrame(collected_edges, schema=[src_col, dst_col], orient="row")


def _build_graph_response(
    sampled: pl.DataFrame, original_total_nodes: int, original_total_edges: int
):
    """Build a sampled NetworkX graph and return the API response dict."""
    G = NetworkAnalysis.create_network_graph(sampled)
    analysis = NetworkAnalysis()
    # Calculate layout using the centralized logic (uses igraph for < 2000 nodes, FA2 > 2000)
    pos = analysis.compute_layout(G)

    # Community detection
    communities = NetworkCommunities.networkCommunities(G)
    node_to_community: dict[str, int] = {}
    for i, comm in enumerate(communities):
        for node in comm:
            node_to_community[node] = i

    nodes = [
        {
            "id": str(node),
            "x": float(pos[node][0]),
            "y": float(pos[node][1]),
            "community": node_to_community.get(node, 0),
            "degree": G.degree(node),
        }
        for node in G.nodes()
    ]

    edges = [
        {
            "source": str(u),
            "target": str(v),
            "weight": float(d.get("weight", 1.0)),
        }
        for u, v, d in G.edges(data=True)
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "metrics": {
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "num_communities": len(communities),
            "total_nodes_in_dataset": original_total_nodes,
            "total_edges_in_dataset": original_total_edges,
            "sample_coverage_pct": round(G.number_of_edges() / original_total_edges * 100, 2),
        },
    }


class MetricRequest(BaseModel):
    metric_name: str


# ---------------------------------------------------------------------------
# GET /graph/sample
# ---------------------------------------------------------------------------

_STRATEGIES = {"random", "degree_weighted", "snowball"}


@router.get("/sample")
def get_graph_sample(
    n_edges: int = Query(default=500, ge=10, le=20000, description="Number of edges to sample"),
    strategy: str = Query(
        default="degree_weighted",
        description="Sampling strategy: random | degree_weighted | snowball",
    ),
    seed: int = Query(default=42, description="Random seed for reproducibility"),
):
    """
    Returns a fast sampled subgraph from the loaded dataset.

    Strategies:
    - **random**           – pure random edge sample (fastest, ~22 ms for n=500)
    - **degree_weighted**  – induced subgraph of the top-K degree hubs (representative)
    - **snowball**         – BFS from the highest-degree node (most connected subgraph)
    """
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")

    if strategy not in _STRATEGIES:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown strategy '{strategy}'. Choose from: {sorted(_STRATEGIES)}",
        )

    import time

    t0 = time.perf_counter()

    original_total_nodes = pl.concat([data[data.columns[0]], data[data.columns[1]]]).n_unique()
    original_total_edges = len(data)

    try:
        if strategy == "random":
            sampled = _sample_random(data, n_edges, seed)
        elif strategy == "degree_weighted":
            sampled = _sample_degree_weighted(data, n_edges, seed)
        else:  # snowball
            sampled = _sample_snowball(data, n_edges, seed)

        response = _build_graph_response(sampled, original_total_nodes, original_total_edges)
        response["metrics"]["sampling_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        response["metrics"]["strategy"] = strategy
        response["metrics"]["seed"] = seed
        return response

    except Exception as e:
        logger.exception("Error in /graph/sample")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layout")
def get_graph_layout():
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")

    try:
        # Create the graph using our new filter
        G = NetworkAnalysis.create_network_graph(data)

        # Calculate layout
        analysis = NetworkAnalysis()
        pos = analysis.compute_large_layout(G)

        # Calculate communities for coloring
        communities = NetworkCommunities.networkCommunities(G)
        node_to_community = {}
        for i, comm in enumerate(communities):
            for node in comm:
                node_to_community[node] = i

        # Format for Sigma.js / React Force Graph
        nodes = []
        for node in G.nodes():
            nodes.append(
                {
                    "id": str(node),
                    "x": float(pos[node][0]),
                    "y": float(pos[node][1]),
                    "community": node_to_community.get(node, 0),
                    "degree": G.degree(node),
                }
            )

        edges = []
        # Sample edges to avoid overwhelming the browser payload if still too large
        for u, v, d in G.edges(data=True):
            edges.append(
                {"source": str(u), "target": str(v), "weight": float(d.get("weight", 1.0))}
            )

        return {
            "nodes": nodes,
            "edges": edges,
            "metrics": {
                "num_nodes": G.number_of_nodes(),
                "num_edges": G.number_of_edges(),
                "num_communities": len(communities),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metric")
def get_graph_metric(req: MetricRequest):
    data = app_state.get_data()
    if data is None:
        raise HTTPException(status_code=400, detail="No data loaded")

    try:
        G = NetworkAnalysis.create_network_graph(data)
        metric = req.metric_name

        result = None

        if metric == "Number of Nodes":
            result = networkStatistics.numberofNodes(G)  # noqa: E701
        elif metric == "Number of Edges":
            result = networkStatistics.numberofEdges(G)  # noqa: E701
        elif metric == "Maximum Degree":
            result = networkStatistics.maximumDegree(G)  # noqa: E701
        elif metric == "Minimum Degree":
            result = networkStatistics.minumumDegree(G)  # noqa: E701
        elif metric == "Average Degree":
            result = networkStatistics.averageDegree(G)  # noqa: E701
        elif metric == "Assortativity":
            result = networkStatistics.assortativity(G)  # noqa: E701
        elif metric == "Number of triangles":
            result = networkStatistics.numberOfTriangles(G)  # noqa: E701
        elif metric == "Network Degree":
            result = networkStatistics.networkDegree(G)  # noqa: E701
        elif metric == "Network Density":
            result = networkStatistics.networkDensity(G)  # noqa: E701
        elif metric == "Network Diameter":
            result = networkStatistics.networkDiameter(G)  # noqa: E701
        elif metric == "Network Radius":
            result = networkStatistics.networkRadius(G)  # noqa: E701
        elif metric == "Network Average Clustering":
            result = networkStatistics.networkAverageClustering(G)  # noqa: E701
        elif metric == "Network Average Degree Conectivity":
            result = networkStatistics.networkAverageDegreeConectivity(G)  # noqa: E701
        elif metric == "Network Average Path Length":
            result = networkStatistics.networkAveragePathLength(G)  # noqa: E701
        elif metric == "Network Degree Distribution":
            result = networkStatistics.networkDegreeDistribution(G)  # noqa: E701
        elif metric == "Network Clustering Coefficient":
            result = networkStatistics.networkClusteringCoefficient(G)  # noqa: E701
        elif metric == "Network Communities":
            result = [list(c) for c in NetworkCommunities.networkCommunities(G)]  # noqa: E701
        elif metric == "Network Modularity":
            result = NetworkCommunities.networkModularity(G)  # noqa: E701
        elif metric == "Number of Communities":
            result = NetworkCommunities.NoOfCommunities(G)  # noqa: E701
        elif metric == "Network Community Size":
            result = NetworkCommunities.networkCommunitySize(G)  # noqa: E701
        elif metric == "Network Key Nodes":
            result = NetworkCommunities.networkKeyNodes(G)  # noqa: E701
        elif metric == "Community Leader Nodes":
            result = NetworkCommunities.communityLeaderNodes(G)  # noqa: E701
        elif metric == "Network Isolates":
            result = NetworkCommunities.networkIsolates(G)  # noqa: E701
        elif metric == "Network Degree Centrality":
            result = NetworkCommunities.networkDegreeCentrality(G)  # noqa: E701
        elif metric == "Network Betweenness Centrality":
            result = NetworkCommunities.networkBetweennessCentrality(G)  # noqa: E701
        elif metric == "Network Closeness Centrality":
            result = NetworkCommunities.networkClosenessCentrality(G)  # noqa: E701
        elif metric == "Network Eigenvector Centrality":
            result = NetworkCommunities.networkEigenvectorCentrality(G)  # noqa: E701
        elif metric == "Network PageRank":
            result = NetworkCommunities.networkPageRank(G)  # noqa: E701
        else:
            raise HTTPException(status_code=400, detail="Unknown metric")

        return {"metric": metric, "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
