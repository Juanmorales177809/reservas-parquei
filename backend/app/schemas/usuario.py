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
    """Permite al admin asignar un rol al crear un usuario."""

    rol: Rol = Rol.USUARIO
    espacio_id: int | None = None


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


class LoginResponse(BaseModel):
    """Respuesta de `POST /auth/login` tras el corte 9G (cookie-only).

    La sesión viaja en la cookie HttpOnly `access_token` que fija
    `app/api/auth.py`; el body ya no expone el JWT ni `token_type`.
    """

    user: UsuarioResponse
