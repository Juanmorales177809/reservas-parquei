from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import Rol, VinculacionUsuario


class UsuarioLaboratorioResponse(BaseModel):
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


class UsuarioUpdate(BaseModel):
    """Body de `PUT /usuarios/{id}` (admin, rol `usuario` únicamente desde
    la separación en `personal`/`usuarios` -- sin `rol`/`espacio_id`, que
    ya no aplican acá; ver `schemas/personal.py::PersonalCreate/Update`
    para admin/gestor)."""

    username: str | None = Field(default=None, min_length=3, max_length=80)
    email: str | None = Field(default=None, max_length=255)
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
    # Correo opcional (2026-09-03), independiente del toggle de laboratorio
    # -- ver `services/preferencias_correo.py`. Opcional acá: no bloquea el
    # guard de perfil incompleto, solo se manda si la persona lo toca.
    recibir_correos: bool | None = None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    rol: Rol
    laboratorio: UsuarioLaboratorioResponse | None = None
    documento_identificacion: str | None = None
    telefono: str | None = None
    institucion: str | None = None
    vinculacion: VinculacionUsuario | None = None
    dependencia: str | None = None
    recibir_correos: bool = True


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


class RegistroRequest(BaseModel):
    """Body de `POST /auth/registro` (público, sin autenticación).

    Autoregistro abierto (2026-08-28, decisión explícita del usuario del
    proyecto): cualquiera crea su propia cuenta con rol `usuario`, sin
    aprobación de un admin -- excepción deliberada al diseño previo de
    "solo un admin invita" (ver el docstring de `supabase_sesion` en
    `app/api/auth.py`, que sigue vigente para el resto de los casos: este
    endpoint nunca busca ni vincula una cuenta existente por email, solo
    crea una nueva). A diferencia de `UsuarioCreate` (sin `password`
    porque la identidad la crea un admin vía invitación), acá la persona
    elige su propia contraseña en el mismo formulario.
    """

    username: str = Field(min_length=3, max_length=80)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("El email debe tener un formato válido")
        return value


class RecuperarPasswordRequest(BaseModel):
    """Body de `POST /auth/recuperar` (público). Mismo validador de formato
    que `UsuarioCreate.email` -- no valida si la cuenta existe, eso lo
    decide Supabase del lado del servidor (ver
    `app/services/supabase_admin.py::generar_link_recuperacion`)."""

    email: str = Field(max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("El email debe tener un formato válido")
        return value
