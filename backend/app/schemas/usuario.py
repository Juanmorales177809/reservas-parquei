from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import Rol


class UsuarioEspacioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    ubicacion: str


class UsuarioCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: str = Field(max_length=255)
    # 72 = límite real de bcrypt (passlib+bcrypt trunca en silencio pasado
    # ese byte); ver backend/CLAUDE.md sobre el pineo de bcrypt==3.2.2.
    password: str = Field(min_length=6, max_length=72)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("El email debe tener un formato válido")
        return value


class AdminUsuarioCreate(UsuarioCreate):
    """Permite al admin asignar un rol al crear un usuario.

    `password` se acepta por compatibilidad con clientes que aún la envíen,
    pero SIEMPRE se ignora: la contraseña real la genera el backend
    (`create_usuario_admin` en `app/api/usuarios.py`) y se entrega por
    correo, nunca la elige quien crea el usuario.
    """

    rol: Rol = Rol.USUARIO
    espacio_id: int | None = None
    password: str | None = Field(default=None, min_length=6, max_length=72)


class UsuarioLogin(BaseModel):
    # 80 = mismo máximo ya usado para username en Create/Update; 72 = límite
    # real de bcrypt para password (ver UsuarioCreate.password arriba).
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=72)

class UsuarioUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=80)
    email: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=6, max_length=72)
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
    # True si la contraseña actual es una temporal generada por el backend
    # (alta de usuario o recuperación): el cliente debe forzar el cambio
    # antes de dejar navegar a cualquier otra pantalla.
    debe_cambiar_password: bool = False


class LoginResponse(BaseModel):
    """Respuesta de `POST /auth/login` tras el corte 9G (cookie-only).

    La sesión viaja en la cookie HttpOnly `access_token` que fija
    `app/api/auth.py`; el body ya no expone el JWT ni `token_type`.
    """

    user: UsuarioResponse


class CambiarPasswordRequest(BaseModel):
    """Body de `POST /auth/cambiar-password` (usuario autenticado).

    Exige la contraseña actual (aunque sea la temporal recién recibida por
    correo) como confirmación -- evita que una sesión ya autenticada pueda
    cambiar la contraseña sin que quien la use la conozca.
    """

    password_actual: str = Field(min_length=1, max_length=72)
    password_nueva: str = Field(min_length=6, max_length=72)


class SolicitarRecuperacionRequest(BaseModel):
    """Body de `POST /auth/recuperar` (público). Acepta username o email
    indistintamente -- ver `get_usuario_by_username`/`get_usuario_by_email`."""

    identificador: str = Field(min_length=1, max_length=255)


class RestablecerPasswordRequest(BaseModel):
    """Body de `POST /auth/restablecer` (público)."""

    identificador: str = Field(min_length=1, max_length=255)
    codigo: str = Field(min_length=6, max_length=6)
    password_nueva: str = Field(min_length=6, max_length=72)


class SupabaseSesionRequest(BaseModel):
    """Body de `POST /auth/supabase/sesion` (hybrid, SUPABASE_ENABLED).

    El cliente Flutter tras `supabase.auth.signIn()` obtiene un JWT cuyo
    `sub` es el UUID de `auth.users`. Este endpoint verifica ese JWT con
    `SUPABASE_JWT_SECRET`, vincula `usuarios.supabase_id` por email (auto-link
    en el primer login) y fija la cookie `access_token` con el MISMO token
    de Supabase -- así el resto de la API sigue leyendo solo la cookie.
    """

    supabase_token: str = Field(min_length=10, max_length=4096)
