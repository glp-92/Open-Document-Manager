# Open Document Manager

Open Document Manager es una aplicación para gestionar workspaces documentales, cargar archivos a almacenamiento S3 compatible, indexarlos para búsqueda semántica y consultarlos desde una interfaz web con chat asistido por LLM.

El proyecto está organizado como un monorepo con estos bloques principales:

- `frontend`: interfaz React para workspaces, documentos y chat.
- `api`: API FastAPI para gestión de workspaces, documentos, chats y mensajería.
- `vector-index`: servicio de indexación y consulta semántica basado en [LEANN](https://github.com/yichuan-w/LEANN)
- `storage`: almacenamiento S3 compatible con SeaweedFS.
- `db`: base de datos PostgreSQL.
- `ollama-server`: servicio para modelos de embeddings y generación.

# Setup Y Requerimientos

## Uso sin desarrollo local

Requisitos

- Docker
- Docker Compose
- Un archivo `.env` basado en `.env.example`

Pasos mínimos:

```bash
cp .env.example .env
docker compose up --build
```

## Desarrollo local

Si además quieres desarrollar sobre el proyecto, necesitas también:

- Python `3.14` para `api`
- Python `3.12` para `vector-index`
- Node.js para `frontend`
- `uv` para gestionar dependencias Python
- Docker Compose para servicios de infraestructura

Variables relevantes en `.env`:

- `DB_USR`, `DB_PWD`, `DB_NAME`
- `STORAGE_HOST`, `STORAGE_PORT`, `STORAGE_PUBLIC_URL`
- `STORAGE_USR`, `STORAGE_PWD`, `STORAGE_BUCKET`
- `OLLAMA_URL`, `LLM_MODEL`, `EMBEDDING_MODEL`

## Servicios expuestos

- Frontend: `http://localhost:3000`
- API: `http://localhost:8080/api`
- Ollama: `http://localhost:11434`
- SeaweedFS S3: `http://localhost:9000`
- SeaweedFS panel: `http://localhost:8888`
- PostgreSQL dashboard: `http://localhost:8081`

# Instrucciones De Uso

## Arranque

```bash
cp .env.example .env
docker compose up --build
```

## Abrir el frontend

Accede a:

```text
http://localhost:3000
```

## Flujo básico

1. Crea un workspace desde la interfaz.
2. Sube uno o varios documentos.
3. Espera a que el sistema procese e indexe el contenido.
4. Abre o crea un chat dentro del workspace.
5. Haz preguntas sobre los documentos cargados.

## Notas mínimas de uso

- El frontend depende de que la API, PostgreSQL, SeaweedFS y `vector-index` estén disponibles.
- Los documentos se almacenan en el servicio S3 compatible y se indexan para búsqueda semántica.
- El chat renderiza respuestas con Markdown.
- Si no hay workspaces seleccionados, el chat no permite enviar mensajes.

## Parada de servicios

```bash
docker compose down
```

Si quieres conservar los datos, no elimines los directorios persistidos del proyecto.
