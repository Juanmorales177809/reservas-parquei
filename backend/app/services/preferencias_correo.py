"""Correo opcional (2026-09-03): dos niveles independientes.

`Laboratorio.notificar_por_correo` apaga TODO correo de reservas de ese
laboratorio, para cualquier destinatario. `Personal.recibir_correos` /
`Usuario.recibir_correos` es la preferencia de cada persona, independiente
del laboratorio. Ambos deben estar activos para que un correo de reserva
salga -- ninguno de los dos gatea la `Notificacion` in-app, solo el correo.
"""

from app.models.laboratorio import Laboratorio
from app.models.personal import Personal
from app.models.usuario import Usuario


def correo_habilitado(laboratorio: Laboratorio, destinatario: Personal | Usuario) -> bool:
    if not laboratorio.notificar_por_correo:
        return False
    return destinatario.recibir_correos
