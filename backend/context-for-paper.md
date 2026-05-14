# Abstract

The advent of massive complex networks demands highly performant, portable, and intelligent data analysis frameworks. This document outlines the architecture and technical implementation of NEDAF (Network Data Analysis Framework), a modernized web-based system designed to process, visualize, and reason over large-scale graph data. NEDAF integrates ultra-fast data manipulation via Polars, high-performance graph metrics using igraph, WebGL-based visualization, and offline Small Language Model (SLM) inferencing for automated, privacy-preserving insights. The system is fully containerized, ensuring universal reproducibility and deployment via GitHub Container Registry.

---

# 1. Introduction
Traditional network analysis tools often face bottlenecks when handling large-scale datasets, particularly in web environments where memory and rendering threads are constrained. NEDAF addresses these limitations by decoupling heavy computational tasks from the client, employing a high-performance backend architecture, progressive data sampling, and edge-AI integration. The framework is designed to provide researchers with a seamless transition from raw data ingestion to complex statistical distribution, network metric computation, and AI-driven topological insights.

# 2. System Architecture
The framework adopts a decoupled microservices architecture, dockerized for cross-platform compatibility.

## 2.1. High-Performance Backend (FastAPI + Polars)
The core computational engine is built on Python 3.12 using the **FastAPI** framework, ensuring asynchronous, non-blocking RESTful communication. 
- **Data Engine:** Instead of relying on traditional Pandas DataFrames, NEDAF utilizes **Polars**, an ultra-fast, multi-threaded DataFrame library written in Rust. This allows for parallelized execution of descriptive statistics (e.g., correlation matrices, exact histogram binning).
- **Network Processing:** Graph computations are handled by a hybrid approach combining **NetworkX** for structural graph logic and **igraph** (compiled in C) for computationally expensive operations such as community detection (Louvain algorithm) and Force-Directed layout approximations (e.g., Fruchterman-Reingold).

## 2.2. Interactive Frontend (React + WebGL)
The client-side application is developed using **React and TypeScript**, bundled with Vite for optimized chunking.
- **Data Visualization:** Statistical distributions are rendered using **Recharts**, with data being pre-binned by the backend to prevent DOM overload.
- **Graph Rendering:** For large network topologies, NEDAF employs **WebGL** (via libraries such as `react-force-graph-2d`). This bypasses the traditional DOM and uses the GPU, allowing fluid interaction with networks containing thousands of nodes.
- **UX/UI:** The interface implements a modern "Glassmorphism" aesthetic with strict state management, providing a cognitive-friendly environment for complex data exploration.

# 3. Methodological Advancements

## 3.1. Progressive Sampling and Distribution Mapping
To achieve sub-second responsiveness on massive datasets, NEDAF implements algorithmic sampling. 
- **Statistical Binning:** Continuous numerical distributions are grouped dynamically on the backend using `polars.Series.hist()`, ensuring the frontend only receives necessary structural intervals rather than millions of flat coordinate points.
- **Graph Sampling:** For graphs exceeding rendering limits, NEDAF implements strategic subgraph sampling (e.g., Degree-Weighted, Snowball, or Random sampling) ensuring that visual density is reduced while preserving the fundamental structural properties (hubs, modularity) of the original network.

## 3.2. Offline Edge AI Integration (Graph-RAG)
A novel feature of NEDAF is its autonomous reasoning module, designed to provide Graph Theory insights without compromising data privacy.
- **Small Language Models (SLM):** The framework integrates **Phi-3-Mini** (a highly capable 3.8B parameter model by Microsoft) deployed locally via **Ollama**.
- **Retrieval-Augmented Generation (RAG):** The integration utilizes `langchain_community` to inject precise deterministic metrics calculated by the backend (e.g., global clustering coefficient, degree distribution, node counts) into the SLM's context window. This prevents mathematical hallucinations, allowing the AI to offer grounded, expert-level interpretations of the network's topology in real time.

# 4. Deployment and Reproducibility
Scientific software often suffers from complex local environment dependencies. NEDAF guarantees universal reproducibility through:
- **Full Containerization:** The system is composed of three interconnected Docker containers (Frontend via Nginx, Backend via Uvicorn, and AI via Ollama).
- **Dependency Isolation:** The Python environment uses a highly strict `requirements-docker.txt` that strips away local CUDA/NVIDIA overheads, ensuring the container remains lightweight and executable on standard CPU servers.
- **CI/CD Distribution:** GitHub Actions automatically compile and push multi-architecture images to the GitHub Container Registry (GHCR), allowing researchers to deploy the entire framework with a single `docker compose up` command.

# 5. Conclusion
By fusing Rust-based data processing, C-based graph analytics, GPU-accelerated frontend rendering, and local edge AI, NEDAF establishes a new benchmark for web-based network analysis frameworks. It abstracts technical complexities, allowing researchers to focus entirely on graph theory exploration and insight generation.
