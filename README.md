# vialBot 🇨🇴

Asistente conversacional impulsado por RAG que responde preguntas sobre el **Código Nacional de Tránsito de Colombia** de forma cercana y natural, como si hablaras con un amigo experto en tránsito.

## Características

- 💬 **Conversacional**: tono amigable, usa emojis con moderación y explica sin tecnicismos.
- 🧠 **Memoria**: recuerda el hilo de conversación gracias a checkpoints en PostgreSQL.
- ⚡ **Streaming**: las respuestas aparecen palabra por palabra, como en ChatGPT.
- 🔒 **Seguro**: autenticación JWT con AWS Cognito.
- 📚 **RAG con LangGraph**: recupera información del texto oficial del Código Nacional de Tránsito.

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | React 19 + Vite + Tailwind CSS |
| Backend | FastAPI + Python 3.12 |
| Orquestación RAG | LangGraph |
| Vector DB | Qdrant Cloud (o Qdrant local para desarrollo) |
| Embeddings | Google Gemini `models/gemini-embedding-001` (3072-d) |
| LLM | Google Gemini `gemini-2.5-flash` |
| Memoria | PostgreSQL + `langgraph-checkpoint-postgres` |
| Auth | AWS Cognito (JWT RS256) |

## Requisitos

- Python 3.12+
- Node.js 20+
- uv
- Docker y Docker Compose
- API key de Google AI Studio / Google Cloud (para Gemini)
- Cuenta de AWS con Cognito User Pool (para producción; en local puedes deshabilitar auth)

## Estructura

```
vialBot/
├── backend/          # FastAPI + LangGraph + ingestión
├── frontend/         # React + Vite + chat UI
├── data/             # PDF del Código Nacional de Tránsito
├── docker-compose.yml
└── README.md
```

## Configuración

1. Copia los archivos de ejemplo:

```bash
cp .env.example backend/.env
cp .env.example frontend/.env.local
```

2. Completa las variables en `backend/.env` y `frontend/.env.local`:
   - `GOOGLE_API_KEY`: API key de Google AI Studio
   - `COGNITO_*`: datos de tu User Pool (o `AUTH_DISABLED=true` / `VITE_AUTH_DISABLED=true` para desarrollo)

3. Levanta los servicios locales:

```bash
docker compose up -d postgres qdrant
```

## Ingesta del PDF

El PDF de la Ley 769 de 2002 ya se encuentra en `data/codigo_nacional_transito.pdf`. Para indexarlo en Qdrant:

```bash
cd backend
source .venv/bin/activate
python -m app.ingestion.index ../data/codigo_nacional_transito.pdf
```

Esto creará la colección en Qdrant e indexará los chunks con embeddings de Gemini.

## Ejecutar backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

La API estará en `http://localhost:8000`.

## Ejecutar frontend

```bash
cd frontend
npm install
npm run dev
```

La aplicación estará en `http://localhost:5173`.

## Endpoints principales

- `GET /health` — Health check
- `POST /chat` — Enviar mensaje y obtener respuesta completa (requiere Bearer JWT)
- `POST /chat/stream` — Enviar mensaje y obtener respuesta en streaming vía SSE
- `POST /admin/ingest` — Re-indexar el PDF (requiere header `X-Admin-Key`)

## Desarrollo sin Cognito

Para probar localmente sin Cognito, establece:

```env
# backend/.env
AUTH_DISABLED=true

# frontend/.env.local
VITE_AUTH_DISABLED=true
```

El backend aceptará cualquier token Bearer y el frontend no redirigirá al login.

## Configuración de Cognito

1. Crea un **User Pool** en AWS Cognito.
2. Configura un **App Client** con flujo OAuth2 y `redirect_uri` de tu frontend.
3. Establece `COGNITO_REGION`, `COGNITO_USER_POOL_ID` y `COGNITO_APP_CLIENT_ID` en `backend/.env`.
4. Establece `VITE_COGNITO_DOMAIN`, `VITE_COGNITO_CLIENT_ID` y `VITE_COGNITO_REDIRECT_URI` en `frontend/.env.local`.

## Despliegue

- **Frontend**: Vercel, Netlify, S3 + CloudFront.
- **Backend**: ECS Fargate, Railway, Render o cualquier servicio de contenedores.
- **Base de datos**: Qdrant Cloud + PostgreSQL administrado (RDS, Supabase, etc.).

## Aviso legal

vialBot es una herramienta orientativa. La información proporcionada debe verificarse siempre contra la norma oficial vigente.
