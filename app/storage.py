import os
from pathlib import Path
from typing import Optional

# Directory where generated models are stored.
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

def save_model(job_id: str, data: bytes) -> Path:
    """Persist the model bytes to disk.

    In production this would upload to a secure object store (e.g., S3) and
    return a presigned URL. For the purposes of this repository we store the
    file locally under ``models/``.
    """
    path = MODEL_DIR / f"{job_id}.glb"
    path.write_bytes(data)
    return path

def get_model_path(job_id: str) -> Optional[Path]:
    """Return the path to the stored model if it exists."""
    path = MODEL_DIR / f"{job_id}.glb"
    return path if path.exists() else None
