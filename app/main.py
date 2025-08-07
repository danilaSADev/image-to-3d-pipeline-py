"""FastAPI application that proxies Stability AI's image-to-3D generation."""
from __future__ import annotations

import os
import uuid

import httpx
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from .auth import verify_jwt
from .storage import get_model_path, save_model

app = FastAPI(title="Image to 3D API")

STABILITY_API_URL = "https://api.stability.ai/vX/3d/generate"


@app.post("/generate")
async def generate_3d_model(
    image: UploadFile = File(...),
    _claims: dict = Depends(verify_jwt),
) -> dict:
    """Accept an image and return a URL to the generated 3D model."""
    if image.content_type not in {"image/png", "image/jpeg"}:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Stability API key not configured")

    job_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            STABILITY_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            files={"image": (image.filename, await image.read(), image.content_type)},
        )
    response.raise_for_status()

    save_model(job_id, response.content)
    return {"job_id": job_id, "model_url": f"/asset/{job_id}"}


@app.get("/asset/{job_id}")
async def get_asset(job_id: str, _claims: dict = Depends(verify_jwt)) -> FileResponse:
    """Return the stored 3D model for ``job_id``."""
    path = get_model_path(job_id)
    if not path:
        raise HTTPException(status_code=404, detail="Model not found")
    return FileResponse(path)
