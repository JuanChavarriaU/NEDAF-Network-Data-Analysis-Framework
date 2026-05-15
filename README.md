# NEDAF (Network Data Analysis Framework)

NEDAF es una aplicación integral para el análisis de redes, visualización interactiva y consulta a través de Inteligencia Artificial (LLM). Este monorepo contiene tanto el backend (FastAPI) como el frontend (React), diseñados para operar de forma conjunta a través de contenedores Docker.

## Estructura del Proyecto

- `backend/`: API construida con FastAPI, procesamiento de grafos (NetworkX) y LangChain.
- `frontend/`: Interfaz de usuario construida con React, TypeScript y renderizado WebGL para grandes redes.
- `docker-compose.yml`: Orquestador principal del código fuente para desarrollo local.
- `.github/workflows/`: Pipelines de CI/CD para la generación y publicación automática de imágenes Docker.

---

## 🚀 Despliegue (Servidor, VPS o Local)

Existen dos estrategias principales de despliegue. La **Opción 1** es ideal para entornos productivos (VPS/Servidores) consumiendo imágenes ya construidas. La **Opción 2** es ideal para entornos de desarrollo local.

### Opción 1: Despliegue en Servidor/VPS con GHCR 


Para desplegar en tu servidor **sin necesidad de descargar el código fuente**, sigue estos pasos:


1. **Crear el archivo `docker-compose.yml` en el servidor**:
   En tu VPS o servidor, crea un directorio para NEDAF y dentro de él un archivo llamado `docker-compose.yml` con el siguiente contenido. *(Importante: Reemplaza `tu-usuario` y `nombre-del-repo` por los correspondientes en GitHub)*:

   ```yaml
   services:
     nedaf-backend:
       image: ghcr.io/tu-usuario/nombre-del-repo-backend:latest
       container_name: nedaf-backend
       ports:
         - "8000:8000"
       environment:
         - OLLAMA_HOST=http://nedaf-ai:11434
       depends_on:
         - nedaf-ai
       networks:
         - nedaf-network
       restart: unless-stopped

     nedaf-frontend:
       image: ghcr.io/tu-usuario/nombre-del-repo-frontend:latest
       container_name: nedaf-frontend
       ports:
         - "80:80"
       depends_on:
         - nedaf-backend
       networks:
         - nedaf-network
       restart: unless-stopped

     nedaf-ai:
       image: ollama/ollama:latest
       container_name: nedaf-ai
       ports:
         - "11434:11434"
       volumes:
         - ollama_data:/root/.ollama
       networks:
         - nedaf-network
       restart: unless-stopped
       # Descarga el modelo automáticamente si no existe
       entrypoint: >
         /bin/sh -c "
         /bin/ollama serve &
         sleep 5 &&
         /bin/ollama pull phi3:mini &&
         wait
         "

   networks:
     nedaf-network:
       driver: bridge

   volumes:
     ollama_data:
   ```

3. **Levantar los contenedores**:
   En el mismo directorio donde creaste el archivo, ejecuta:
   ```bash
   docker-compose up -d
   ```
   *La aplicación estará disponible en el puerto `80` (Frontend) y `8000` (Backend).* Para actualizar, simplemente haz `docker-compose pull` y luego `docker-compose up -d` de nuevo.

---

### Opción 2: Despliegue Local Construyendo el Código (Recomendado para Desarrollo)

Si deseas probar el código, modificarlo o probar localmente con Docker:

1. Clona este repositorio y navega a la raíz:
   ```bash
   git clone https://github.com/tu-usuario/nombre-del-repo.git
   cd nombre-del-repo
   ```

2. Ejecuta el orquestador principal que compilará las imágenes a partir del código local:
   ```bash
   docker-compose up --build -d
   ```

3. Accede a tu aplicación:
   - Frontend: `http://localhost:80`
   - Backend API: `http://localhost:8000/docs`
