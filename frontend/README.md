# NEDAF Web (Frontend)

El frontend de NEDAF es una SPA (Single Page Application) moderna y reactiva construida con **React**, **TypeScript** y el empaquetador **Vite**. Su principal propósito es proveer una interfaz visual intuitiva y un renderizado de redes de gran escala sin pérdida de frames utilizando tecnologías basadas en **WebGL**.

## Tecnologías Principales

- **React 18 + TypeScript**: Lógica base fuertemente tipada.
- **Vite**: Motor de compilación en desarrollo y empaquetador para producción.
- **react-force-graph-2d**: Manejo avanzado del grafo a través de la tarjeta gráfica (WebGL) para evitar bloqueos en el hilo principal de JavaScript.
- **Axios**: Clientes y servicios consumibles conectados al Backend (FastAPI).
- **TailwindCSS**: Estilizado moderno para la interfaz gráfica.

## Estructura

- `src/`: Contiene todo el código base (componentes, servicios API, estilos).
- `src/services/api.ts`: Centraliza la conexión al Backend.
- `Dockerfile`: Orquesta un entorno Node.js y expone los compilados mediante un servidor web NGINX liviano.

## Desarrollo Local

Si deseas modificar la interfaz o los estilos de manera local sin usar Docker:

1. Instala las dependencias:
   ```bash
   npm install
   ```

2. Ejecuta el servidor de desarrollo de Vite:
   ```bash
   npm run dev
   ```

Tu aplicación interactiva estará corriendo localmente en `http://localhost:5173`. Recuerda tener el backend corriendo simultáneamente para que la aplicación obtenga los datos y métricas necesarias.
