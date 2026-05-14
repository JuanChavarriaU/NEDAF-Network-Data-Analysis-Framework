FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for igraph and other C-extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libglpk-dev \
    libgmp3-dev \
    libblas-dev \
    liblapack-dev \
    libarpack2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements*.txt ./

# Copy the clean docker requirements
COPY requirements-docker.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
