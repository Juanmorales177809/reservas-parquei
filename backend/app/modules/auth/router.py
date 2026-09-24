"""Router de auth. Hoy solo `GET /api/auth/csrf` (BK-06); el resto de
endpoints del contrato se construye en `BK-09` / `specs/modules/auth/tasks.md`.
"""

from fastapi import APIRouter, Request, Response

from app.core.security import asegurar_cookie_csrf

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/csrf", status_code=204)
def obtener_csrf(request: Request, response: Response) -> None:
    """Contrato §3.0: emite `rp_csrf` sin exigir sesión. Idéntica exista o no una."""
    asegurar_cookie_csrf(request, response)
