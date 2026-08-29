from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import Personal, Usuario
from app.schemas.lista_espera import ListaEsperaCreate, ListaEsperaResponse
from app.services.lista_espera import cancelar, crear_entrada, listar_mias


router = APIRouter(prefix="/lista-espera", tags=["lista-espera"])


@router.post("", response_model=ListaEsperaResponse, status_code=201)
def crear_entrada_endpoint(
    data: ListaEsperaCreate,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    return crear_entrada(db, data, current_user)


@router.get("/mias", response_model=list[ListaEsperaResponse])
def listar_mias_endpoint(
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    return listar_mias(db, current_user)


@router.delete("/{entrada_id}", status_code=204)
def cancelar_endpoint(
    entrada_id: int,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    cancelar(db, entrada_id, current_user)
    return None
