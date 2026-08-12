from pydantic import BaseModel, ConfigDict, Field, field_validator


class UsuarioEspacioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    ubicacion: str


class UsuarioCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6)


class AdminUsuarioCreate(UsuarioCreate):
    """Permite al admin asignar un rol al crear un usuario."""

    rol: str = Field(default="usuario", pattern="^(admin|gestor|usuario)$")
    espacio_id: int | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("El email debe tener un formato válido")
        return value


class UsuarioLogin(BaseModel):
    username: str
    password: str

class UsuarioUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=80)
    email: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=6)
    rol: str | None = Field(default=None, pattern="^(admin|gestor|usuario)$")
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
    rol: str
    espacio: UsuarioEspacioResponse | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioResponse
