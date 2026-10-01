FROM python:3.12-slim
WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sin privilegios de root. Los adjuntos de lista de espera se guardan en /code/storage: se crea aquí, con su
# dueño, para que el volumen con nombre que lo monta herede el permiso al crearse vacío.
RUN useradd --create-home --uid 10001 app \
    && mkdir -p /code/storage/reserva_adjuntos \
    && chown -R app:app /code

COPY --chown=app:app app/ ./app/
USER app

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
