# Mousum Graphics

A full-stack graphic design studio platform pairing a minimalist, dark-themed React frontend with a FastAPI backend that powers AI-assisted design suggestions and generation.

## Overview

Mousum Graphics is built as two independent layers that communicate over a REST API:

- **Frontend** — a React single-page site showcasing studio work (identity, editorial, packaging, motion), built with Vite and plain CSS using a shared design-token system (dark canvas, gold accent).
- **Backend** — a Python service exposing AI-assisted design suggestion and generation endpoints, built with FastAPI.

The two layers are decoupled: the frontend can run against a mocked API during early development, and the backend can be deployed, scaled, and versioned independently of the client.

## Architecture

```
┌─────────────────────────┐        HTTPS / JSON        ┌──────────────────────────┐
│   React Frontend         │ ──────────────────────────▶│   FastAPI Backend         │
│   (Vite, plain CSS)      │◀────────────────────────── │   (AI suggestion engine)  │
└─────────────────────────┘                             └──────────────────────────┘
        │                                                          │
        ▼                                                          ▼
  Static hosting                                          Model inference / storage
  (Vercel, Netlify, etc.)                                 (self-hosted or managed)
```

- The frontend never calls AI providers directly — all generation requests are proxied through the backend, keeping API keys and model logic server-side.
- The backend is stateless per-request by default; add a database layer (e.g. Postgres) if you need to persist generated assets or suggestion history.

## Folder Structure

```
mousum-graphics/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Navbar.css
│   │   │   ├── Hero.jsx
│   │   │   ├── Hero.css
│   │   │   ├── DesignGallery.jsx
│   │   │   ├── DesignGallery.css
│   │   │   ├── Footer.jsx
│   │   │   └── Footer.css
│   │   ├── data/
│   │   │   └── designsData.js
│   │   ├── styles/
│   │   │   └── theme.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── routers/
│   │   │   └── suggestions.py   # AI suggestion/generation endpoints
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   └── services/
│   │       └── ai_engine.py     # Model integration logic
│   ├── requirements.txt
│   └── .env.example
│
└── README.md
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- An API key for whichever AI provider the suggestion engine calls (set via environment variable)

## Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` by default. Set the backend URL the frontend should call in a `.env` file:

```
VITE_API_BASE_URL=http://localhost:8000
```

Build for production:

```bash
npm run build
npm run preview
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## Running Both Together

1. Start the backend first (`uvicorn app.main:app --reload`) so the frontend has something to call.
2. Start the frontend (`npm run dev`) in a separate terminal.
3. Confirm `VITE_API_BASE_URL` in the frontend's `.env` points at the running backend.

## Contributing

- Keep frontend styling changes scoped to the design tokens in `src/styles/theme.css` where possible, rather than hardcoding colors in component CSS.
- Backend endpoints should validate input/output with Pydantic models in `app/models/schemas.py`.

## License

Add your license of choice here.