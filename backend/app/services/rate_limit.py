# -*- coding: utf-8 -*-
"""Rate limiting de POST /auth/login contra fuerza bruta (Fase 9C).

En memoria del proceso, sin dependencia nueva. Aceptable para el despliegue
actual porque `backend/Dockerfile` arranca Uvicorn sin `--workers` (un único
proceso) y `docker-compose.yml` no define réplicas del servicio backend; el
workflow de CI hace lo mismo. NO es una solución distribuida: si en el
futuro el backend corre con varios workers o réplicas, cada uno mantiene su
propio conteo y el límite efectivo se multiplica por esa cantidad de
procesos. Migrar a un backend compartido (Redis u otro) queda fuera de
alcance de esta fase por decisión explícita.
"""

from __future__ import annotations

from collections import OrderedDict
from datetime import timedelta

from app.domain.protocols import Reloj
from app.services.reloj import RelojLocal

LIMITE_INTENTOS_LOGIN = 5
VENTANA_LOGIN = timedelta(minutes=15)
# Cota dura de memoria: número máximo de claves (ip:username) rastreadas a
# la vez. Sin esto, un atacante que varíe IP o username indefinidamente
# podría hacer crecer el diccionario sin límite.
MAX_CLAVES_RASTREADAS = 10_000


class LimitadorIntentosLogin:
    """Ventana deslizante de intentos fallidos, por clave `ip:username`."""

    def __init__(
        self,
        reloj: Reloj | None = None,
        limite: int = LIMITE_INTENTOS_LOGIN,
        ventana: timedelta = VENTANA_LOGIN,
        max_claves: int = MAX_CLAVES_RASTREADAS,
    ) -> None:
        self._reloj = reloj or RelojLocal()
        self._limite = limite
        self._ventana = ventana
        self._max_claves = max_claves
        # OrderedDict para poder expulsar la clave con actividad más antigua
        # cuando se supera _max_claves (cota de memoria).
        self._intentos: OrderedDict[str, list] = OrderedDict()

    @staticmethod
    def _clave(ip: str, username: str) -> str:
        # Sin normalizar: get_usuario_by_username compara username exacto
        # (case-sensitive, sin trim), así que la clave respeta lo mismo.
        return f"{ip}:{username}"

    def _vigentes(self, clave: str) -> list:
        ahora = self._reloj.ahora()
        restantes = [t for t in self._intentos.get(clave, []) if ahora - t < self._ventana]
        if restantes:
            self._intentos[clave] = restantes
            self._intentos.move_to_end(clave)
        elif clave in self._intentos:
            del self._intentos[clave]
        return restantes

    def bloqueado(self, ip: str, username: str) -> bool:
        clave = self._clave(ip, username)
        return len(self._vigentes(clave)) >= self._limite

    def registrar_fallo(self, ip: str, username: str) -> None:
        clave = self._clave(ip, username)
        vigentes = self._vigentes(clave)
        vigentes.append(self._reloj.ahora())
        self._intentos[clave] = vigentes
        self._intentos.move_to_end(clave)
        while len(self._intentos) > self._max_claves:
            self._intentos.popitem(last=False)

    def reiniciar(self, ip: str, username: str) -> None:
        self._intentos.pop(self._clave(ip, username), None)


limitador_login = LimitadorIntentosLogin()

# Instancia SEPARADA de la de login, misma clase: un fallo de recuperación
# de contraseña no debe consumir ni verse afectado por el presupuesto de
# intentos de login del mismo par (ip, identificador), y viceversa.
limitador_recuperacion = LimitadorIntentosLogin()
