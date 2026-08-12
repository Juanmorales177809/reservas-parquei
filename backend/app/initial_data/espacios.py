from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models.espacio import Espacio
from app.db import Base

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

def init_espacios(db: Session):
    # Verificar si ya existen espacios
    espacios_existentes = db.query(Espacio).count()
    if espacios_existentes > 0:
        print("Los espacios ya existen en la base de datos. Saltando inicialización.")
        return
    
    # Datos iniciales de espacios
    espacios_iniciales = [
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
    
    # Crear espacios en la base de datos
    for espacio_data in espacios_iniciales:
        espacio = Espacio(**espacio_data)
        db.add(espacio)
    
    db.commit()
    print(f"Se han creado {len(espacios_iniciales)} espacios iniciales en la base de datos.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_espacios(db)
    finally:
        db.close()
