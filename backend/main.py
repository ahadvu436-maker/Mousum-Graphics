"""
main.py - AI Backend for mousum-graphics-mvp
==============================================

A FastAPI backend that receives prompts/requests from a React frontend
and forwards them to an AI provider (Anthropic's Claude by default).

Setup:
    1. pip install -r requirements.txt
    2. Create a .env file in this directory with:
           ANTHROPIC_API_KEY=your_api_key_here
    3. Run the server:
           uvicorn main:app --reload --port 8000

The React frontend can then POST to:
    http://localhost:8000/api/generate
"""

import os
import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import anthropic

# ---------------------------------------------------------------------------
# Setup & Configuration
# ---------------------------------------------------------------------------

load_dotenv()  # Loads variables from a local .env file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mousum-graphics-mvp-backend")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

if not ANTHROPIC_API_KEY:
    logger.warning(
        "ANTHROPIC_API_KEY is not set. Requests to /api/generate will fail "
        "until you add it to your environment or .env file."
    )

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="mousum-graphics-mvp AI Backend",
    description="Backend API that proxies AI prompt requests from the React frontend.",
    version="1.0.0",
)

# Allow the React dev server (CRA default: 3000, Vite default: 5173) to call this API.
# Add your production frontend URL(s) here as well before deploying.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str = Field(..., description="Either 'user' or 'assistant'.")
    content: str = Field(..., description="The text content of the message.")


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The user's prompt or instruction.")
    system: Optional[str] = Field(
        default=None,
        description="Optional system prompt to steer the AI's behavior.",
    )
    history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Optional prior conversation turns for multi-turn context.",
    )
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    temperature: float = Field(default=1.0, ge=0.0, le=1.0)


class GenerateResponse(BaseModel):
    response: str
    model: str
    stop_reason: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    ai_configured: bool


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    return {"message": "mousum-graphics-mvp AI backend is running."}


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Simple health check the frontend can ping on startup."""
    return HealthResponse(status="ok", ai_configured=client is not None)


@app.post("/api/generate", response_model=GenerateResponse, tags=["AI"])
def generate(request: GenerateRequest):
    """
    Main endpoint for AI prompt requests.

    Accepts a prompt (and optional system prompt / conversation history)
    from the React frontend and returns the AI-generated response.
    """
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI backend is not configured. Set ANTHROPIC_API_KEY on the server.",
        )

    # Build the message list: prior history (if any) + the new user prompt
    messages = []
    if request.history:
        messages.extend({"role": m.role, "content": m.content} for m in request.history)
    messages.append({"role": "user", "content": request.prompt})

    try:
        kwargs = {
            "model": DEFAULT_MODEL,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": messages,
        }
        if request.system:
            kwargs["system"] = request.system

        completion = client.messages.create(**kwargs)

        # Concatenate all text blocks in the response
        text_output = "".join(
            block.text for block in completion.content if block.type == "text"
        )

        return GenerateResponse(
            response=text_output,
            model=completion.model,
            stop_reason=completion.stop_reason,
        )

    except anthropic.APIStatusError as e:
        logger.error(f"Anthropic API error: {e.status_code} - {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=f"AI provider error: {e.message}",
        )
    except anthropic.APIConnectionError as e:
        logger.error(f"Connection error contacting Anthropic API: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach the AI provider. Please try again shortly.",
        )
    except Exception as e:
        logger.exception("Unexpected error during generation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected server error: {str(e)}",
        )


# ---------------------------------------------------------------------------
# Local dev entrypoint (optional — `uvicorn main:app --reload` is preferred)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
