from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import Rol, VinculacionUsuario


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
    # Fase A2 (perfil de usuario): el admin también puede editar estos
    # campos desde la gestión de usuarios, además del self-service de
    # PerfilUpdate más abajo.
    documento_identificacion: str | None = Field(default=None, max_length=30)
    telefono: str | None = Field(default=None, max_length=30)
    institucion: str | None = Field(default=None, max_length=120)
    vinculacion: VinculacionUsuario | None = None
    dependencia: str | None = Field(default=None, max_length=150)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is not None and ("@" not in value or "." not in value.split("@")[-1]):
            raise ValueError("El email debe tener un formato válido")
        return value


class PerfilUpdate(BaseModel):
    """Body de `PUT /usuarios/me` (self-service, cualquier rol autenticado).

    Contiene EXCLUSIVAMENTE los campos de perfil -- nunca `rol`,
    `espacio_id`, `username` ni `email`. `extra="forbid"` hace que mandar
    cualquier otro campo (ej. `{"rol": "admin"}`) sea un 422 de validación,
    no un campo ignorado en silencio: la escalada de privilegios es
    estructuralmente imposible acá, no depende de que el handler se
    acuerde de filtrar. No reusar `UsuarioUpdate` para este endpoint bajo
    ninguna circunstancia -- ver `backend/CLAUDE.md`.
    """

    model_config = ConfigDict(extra="forbid")

    documento_identificacion: str | None = Field(default=None, max_length=30)
    telefono: str | None = Field(default=None, max_length=30)
    institucion: str | None = Field(default=None, max_length=120)
    vinculacion: VinculacionUsuario | None = None
    dependencia: str | None = Field(default=None, max_length=150)


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    rol: Rol
    espacio: UsuarioEspacioResponse | None = None
    documento_identificacion: str | None = None
    telefono: str | None = None
    institucion: str | None = None
    vinculacion: VinculacionUsuario | None = None
    dependencia: str | None = None


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
