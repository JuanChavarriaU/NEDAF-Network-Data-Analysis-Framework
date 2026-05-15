# NEDAF Backend

El backend de NEDAF está construido con **FastAPI** y **Python**. Su arquitectura se encarga de procesar los datos estadísticos, gestionar las transformaciones, generar las visualizaciones y propiedades de la red empleando igraph, y facilitar el razonamiento sobre los grafos a través de un LLM local provisto por **Ollama**.

## Arquitectura

- `api/`: Contiene el punto de acceso de FastAPI (`main.py`) y los enrutadores que exponen los diferentes *endpoints* a los que se conecta el frontend.
- `Model/`: Centraliza toda la lógica de negocio, cálculos estadísticos, transformaciones, persistencia (bases de datos vectoriales) e integraciones (LangChain).
- `Dockerfile`: Orquesta las dependencias nativas requeridas para cálculo científico (numpy, scipy) y levanta la aplicación en un puerto público.

## Requisitos de Desarrollo

- Python 3.10+

## Entorno Local (Sin Docker)

Si deseas desarrollar o depurar código sin utilizar el entorno empaquetado de Docker:

1. Crea y activa un entorno virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Linux/Mac
   # .venv\Scripts\activate   # En Windows
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el servidor de desarrollo:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

La documentación Swagger de la API estará disponible localmente en: `http://localhost:8000/docs`.
