FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chgrp -R 0 /app && chmod -R g+rwX /app

# Usuario no privilegiado. UID fijo 1000 (docker run/compose habituales) pero
# grupo 0/root (coincide con el chgrp -R 0 de arriba, pensado para el patrón
# de UID arbitrario de OpenShift): en ambos entornos el proceso puede leer y
# escribir /app sin necesitar root.
RUN adduser --disabled-password --gecos "" --uid 1000 --ingroup root appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
