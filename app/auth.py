"""Authentication helpers using JWT tokens."""
import os
from typing import Any, Dict

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, Any]:
    """Validate a JWT passed via the Authorization header.

    The JWT is expected to be signed using the secret in ``JWT_SECRET`` with the
    HS256 algorithm.  If the token is invalid or missing, an HTTP 401 is raised.
    """
    token = credentials.credentials
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT secret not configured")
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc
