# -*- coding: utf-8 -*-
"""Unitarias puras de `app/services/preferencias_correo.py::correo_habilitado`
-- sin pasar por la API, sin persistir nada (los objetos ORM no necesitan
estar en sesión para leer/escribir sus atributos en memoria)."""

from app.models.laboratorio import Laboratorio
from app.models.personal import Personal
from app.models.usuario import Usuario
from app.services.preferencias_correo import correo_habilitado


def _laboratorio(*, notificar_por_correo: bool) -> Laboratorio:
    return Laboratorio(nombre="Sala", capacidad=10, notificar_por_correo=notificar_por_correo)


def _usuario(*, recibir_correos: bool) -> Usuario:
    return Usuario(username="u", email="u@example.com", hashed_password="x", recibir_correos=recibir_correos)


def _personal(*, recibir_correos: bool) -> Personal:
    return Personal(username="p", email="p@example.com", rol="gestor", recibir_correos=recibir_correos)


class TestCorreoHabilitado:
    def test_ambos_activos_habilita(self):
        assert correo_habilitado(_laboratorio(notificar_por_correo=True), _usuario(recibir_correos=True)) is True

    def test_laboratorio_apagado_deshabilita_sin_importar_destinatario(self):
        assert correo_habilitado(_laboratorio(notificar_por_correo=False), _usuario(recibir_correos=True)) is False

    def test_destinatario_apagado_deshabilita_sin_importar_laboratorio(self):
        assert correo_habilitado(_laboratorio(notificar_por_correo=True), _usuario(recibir_correos=False)) is False

    def test_ambos_apagados_deshabilita(self):
        assert correo_habilitado(_laboratorio(notificar_por_correo=False), _usuario(recibir_correos=False)) is False

    def test_funciona_igual_para_personal_que_para_usuario(self):
        assert correo_habilitado(_laboratorio(notificar_por_correo=True), _personal(recibir_correos=True)) is True
        assert correo_habilitado(_laboratorio(notificar_por_correo=True), _personal(recibir_correos=False)) is False
