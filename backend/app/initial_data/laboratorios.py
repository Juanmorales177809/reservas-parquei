from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models.laboratorio import Laboratorio
from app.db import Base

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

def init_laboratorios(db: Session):
    # Verificar si ya existen laboratorios
    laboratorios_existentes = db.query(Laboratorio).count()
    if laboratorios_existentes > 0:
        print("Los laboratorios ya existen en la base de datos. Saltando inicialización.")
        return

    # Datos iniciales de laboratorios
    laboratorios_iniciales = [
        {
            "nombre": "Auditorio Principal",
            "ubicacion": "Edificio Central, Primer Piso",
            "capacidad": 200,
            "estado": "activo"
        },
        {
            "nombre": "Sala de Juntas Ejecutiva",
            "ubicacion": "Edificio Administrativo, Segundo Piso",
            "capacidad": 20,
            "estado": "activo"
        },
        {
            "nombre": "Laboratorio de Informática",
            "ubicacion": "Edificio de Ciencias, Tercer Piso",
            "capacidad": 30,
            "estado": "activo"
        },
        {
            "nombre": "Sala de Conferencias",
            "ubicacion": "Edificio Central, Tercer Piso",
            "capacidad": 50,
            "estado": "mantenimiento"
        },
        {
            "nombre": "Auditorio Pequeño",
            "ubicacion": "Edificio de Humanidades, Primer Piso",
            "capacidad": 80,
            "estado": "inactivo"
        },
        {
            "nombre": "Sala de Estudio Grupales",
            "ubicacion": "Biblioteca, Segundo Piso",
            "capacidad": 15,
            "estado": "activo"
        }
    ]

    # Crear laboratorios en la base de datos
    for laboratorio_data in laboratorios_iniciales:
        laboratorio = Laboratorio(**laboratorio_data)
        db.add(laboratorio)

    db.commit()
    print(f"Se han creado {len(laboratorios_iniciales)} laboratorios iniciales en la base de datos.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_laboratorios(db)
    finally:
        db.close()
