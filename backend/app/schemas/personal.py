from pydantic import BaseModel, Field, field_validator

from app.domain.enums import Rol, VinculacionUsuario


class PersonalCreate(BaseModel):
    """Body de `POST /personal` (admin-only): crea una cuenta de personal
    institucional (`admin`/`gestor`) -- separada de `UsuarioCreate` desde
    la división en dos tablas (ver
    `~/.claude/plans/dazzling-wobbling-zebra.md`). Sin `password`, mismo
    motivo que `UsuarioCreate`: la identidad la crea Supabase vía
    invitación."""

    username: str = Field(min_length=3, max_length=80)
    email: str = Field(max_length=255)
    rol: Rol = Rol.GESTOR
    espacio_id: int | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("El email debe tener un formato válido")
        return value

    @field_validator("rol")
    @classmethod
    def validate_rol_personal(cls, value: Rol) -> Rol:
        if value == Rol.USUARIO:
            raise ValueError("POST /personal solo crea cuentas admin o gestor -- usa POST /usuarios para rol usuario")
        return value


class PersonalUpdate(BaseModel):
    """Body de `PUT /personal/{id}` (admin-only).

    `rol` SÍ acepta `usuario` acá (a diferencia de `PersonalCreate`): es
    la señal para degradar esta cuenta a `usuarios` -- `api/personal.py`
    intercepta ese caso ANTES de llamar a
    `crud/personal.py::actualizar_personal` (que nunca ve `rol=usuario`,
    ver su docstring) y lo resuelve con
    `services/migrar_actor.py::degradar_a_usuario`.
    """

    username: str | None = Field(default=None, min_length=3, max_length=80)
    email: str | None = Field(default=None, max_length=255)
    rol: Rol | None = None
    espacio_id: int | None = None
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
