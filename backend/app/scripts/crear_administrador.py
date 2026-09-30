"""Crea (o restablece la contraseña de) una cuenta ADMINISTRADOR de Reservas.

El administrador de Reservas es una cuenta propia, sin ficha en LIA (decisión 2026-09-30, specs/docs/decisions/
origen-externo-estructura-institucional.md). No se crea desde la interfaz, porque para entrar a la interfaz ya
hace falta uno: esta es la única vía de arranque.

La contraseña **no** viaja por argumentos ni por el entorno: se pide por la terminal (no se muestra) o, en un
pipeline, por la entrada estándar. Así no queda en el historial del shell ni en `docker inspect`.

Uso, dentro del contenedor del backend:

    docker exec -it reservas_backend python -m app.scripts.crear_administrador --correo admin@itm.edu.co

Si ya existe una cuenta con ese correo: si es de administrador, se le restablece la contraseña y se reactiva; si
es de otro tipo, se aborta sin tocarla.
"""

from __future__ import annotations

import argparse
import getpass
import sys
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.security import hash_contrasena
from app.db.models.auth import Cuentas
from app.db.session import SessionLocal

_MIN_CONTRASENA = 8
_MAX_CONTRASENA = 64


def _pedir_contrasena() -> str:
    if not sys.stdin.isatty():
        return sys.stdin.readline().rstrip("\r\n")
    primera = getpass.getpass("Contraseña del administrador: ")
    segunda = getpass.getpass("Repítela: ")
    if primera != segunda:
        raise SystemExit("Las contraseñas no coinciden. No se hizo ningún cambio.")
    return primera


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Crea o restablece una cuenta ADMINISTRADOR de Reservas.")
    parser.add_argument("--correo", required=True, help="Correo con el que entrará.")
    args = parser.parse_args(argv)
    correo = args.correo.strip().lower()
    if "@" not in correo:
        print("El correo no es válido.", file=sys.stderr)
        return 2

    contrasena = _pedir_contrasena()
    if not (_MIN_CONTRASENA <= len(contrasena) <= _MAX_CONTRASENA):
        print(f"La contraseña debe tener entre {_MIN_CONTRASENA} y {_MAX_CONTRASENA} caracteres.", file=sys.stderr)
        return 2

    ahora = datetime.now(timezone.utc)
    with SessionLocal() as db:
        cuenta = db.scalar(select(Cuentas).where(Cuentas.correo == correo))
        if cuenta is None:
            db.add(
                Cuentas(
                    correo=correo,
                    password_hash=hash_contrasena(contrasena),
                    tipo_cuenta="ADMINISTRADOR",
                    id_usuario=None,
                    id_persona=None,
                    estado=True,
                    created_at=ahora,
                    updated_at=ahora,
                )
            )
            accion = "creada"
        elif cuenta.tipo_cuenta == "ADMINISTRADOR":
            cuenta.password_hash = hash_contrasena(contrasena)
            cuenta.estado = True
            cuenta.updated_at = ahora
            accion = "restablecida"
        else:
            print(
                f"Ya existe una cuenta {cuenta.tipo_cuenta} con ese correo; no se toca. Usa otro correo.",
                file=sys.stderr,
            )
            return 1
        db.commit()
    print(f"Cuenta de administrador {accion}: {correo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
