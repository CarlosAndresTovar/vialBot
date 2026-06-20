from typing import Annotated

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer(auto_error=False)


class CognitoJWTValidator:
    def __init__(self) -> None:
        self._jwks: dict | None = None
        self.jwks_url = settings.cognito_jwks_url

    async def _fetch_jwks(self) -> dict:
        if self._jwks is not None:
            return self._jwks
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url, timeout=10.0)
            response.raise_for_status()
            self._jwks = response.json()
        return self._jwks

    async def validate(self, token: str) -> dict:
        jwks = await self._fetch_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token sin 'kid'",
            )

        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Clave de firma no encontrada",
            )

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=settings.cognito_app_client_id,
                issuer=(
                    "https://cognito-idp."
                    f"{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}"
                ),
                options={"require": ["exp", "sub"]},
            )
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {exc}",
            ) from exc

        return payload


validator = CognitoJWTValidator()


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
) -> dict:
    if settings.app_env == "development" and getattr(settings, "auth_disabled", False):
        return {"sub": "dev-user", "email": "dev@example.com"}

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no proporcionadas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await validator.validate(credentials.credentials)
