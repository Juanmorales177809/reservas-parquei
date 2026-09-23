from fastapi import FastAPI

app = FastAPI(title="Reservas Parquei")


@app.get("/health")
def health() -> dict[str, str]:
    return {"estado": "ok"}
