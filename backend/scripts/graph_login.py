# -*- coding: utf-8 -*-
"""Login interactivo único para el puente temporal de correo por Graph
(`app/services/email_graph.py`).

Corré esto UNA VEZ (o cada vez que el token cacheado venza) con la persona
dueña de la cuenta `GRAPH_MAIL_SENDER` a mano, lista para completar el
login en cualquier navegador con el código que va a imprimir acá.

USO:

    cd backend
    DATABASE_URL=... SECRET_KEY=... SUPABASE_URL=... SUPABASE_JWT_SECRET=... \
    SUPABASE_SERVICE_ROLE_KEY=... GRAPH_MAIL_SENDER=sgc-lia@itm.edu.co \
    GRAPH_TOKEN_CACHE_PATH=/ruta/al/cache/token_cache.json \
    .venv/Scripts/python.exe -m scripts.graph_login

En el servidor real (contenedor `backend`, mismo volumen `graph_token_cache`
que monta el backend en producción):

    docker compose run --rm backend python -m scripts.graph_login

No hace falta abrir un navegador EN el servidor -- el device code flow solo
pide visitar una URL e ingresar un código desde cualquier dispositivo con
navegador.
"""

from __future__ import annotations

import sys

sys.path.insert(0, ".")

from app.services.email_graph import login_interactivo  # noqa: E402


def main() -> None:
    login_interactivo()


if __name__ == "__main__":
    main()
