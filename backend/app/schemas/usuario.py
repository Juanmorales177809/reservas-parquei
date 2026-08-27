from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import Rol


class UsuarioEspacioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    ubicacion: str


class UsuarioCreate(BaseModel):
    """Sin `password`: la identidad de autenticación la crea Supabase (ver
    `create_usuario_admin` en `app/api/usuarios.py`, vía
    `app/services/supabase_admin.py`) -- nadie, ni quien crea la cuenta,
    elige una contraseña acá."""

    username: str = Field(min_length=3, max_length=80)
    email: str = Field(max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("El email debe tener un formato válido")
        return value


class AdminUsuarioCreate(UsuarioCreate):
    """Permite al admin asignar un rol al crear un usuario."""

    rol: Rol = Rol.USUARIO
    espacio_id: int | None = None


class UsuarioUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=80)
    email: str | None = Field(default=None, max_length=255)
    rol: Rol | None = None
    espacio_id: int | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is not None and ("@" not in value or "." not in value.split("@")[-1]):
            raise ValueError("El email debe tener un formato válido")
        return value


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    rol: Rol
    espacio: UsuarioEspacioResponse | None = None


class ReenviarInvitacionResponse(BaseModel):
    """Respuesta de `POST /usuarios/{id}/reenviar-invitacion`.

    `link` siempre viene (Supabase lo genera aunque no haya SMTP
    configurado); `correo_enviado` distingue si además se pudo entregar
    por correo o si el admin tiene que pasarlo a mano mientras tanto (ver
    `app/services/email.py` -- sin `EMAIL_ENABLED`, el outbox encola pero
    no intenta enviar).
    """

    link: str
    correo_enviado: bool


class LoginResponse(BaseModel):
    """Respuesta de `POST /auth/supabase/sesion`.

    La sesión viaja en la cookie HttpOnly `access_token` (el JWT de Supabase
    tal cual); el body ya no expone ningún token.
    """

    user: UsuarioResponse


class SupabaseSesionRequest(BaseModel):
    """Body de `POST /auth/supabase/sesion` (público).

    El cliente Flutter, tras `supabase.auth.signInWithPassword()`, obtiene
    un JWT cuyo `sub` es el UUID de `auth.users`. Este endpoint lo verifica
    (`deps.decode_token` -- ES256 vía JWKS o HS256 solo para tests, ver ese
    módulo) y busca el `Usuario` por `supabase_id` -- nunca crea ni vincula
    nada (ver el docstring de `supabase_sesion` en `app/api/auth.py`).
    """

    supabase_token: str = Field(min_length=10, max_length=4096)
