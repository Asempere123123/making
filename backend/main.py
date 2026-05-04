import sqlite3
from typing import Literal, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="API de Control de Vehículos")
DB_NAME = "database.db"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_data (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            estado_a INTEGER DEFAULT 0,
            vehiculo_actual TEXT,
            total_vehiculos INTEGER DEFAULT 0,
            total_ligeros INTEGER DEFAULT 0,
            total_pesados INTEGER DEFAULT 0,
            dato1 REAL DEFAULT 0.0,
            dato2 REAL DEFAULT 0.0,
            dato3 REAL DEFAULT 0.0,
            dato4 REAL DEFAULT 0.0,
            dato5 REAL DEFAULT 0.0,
            dato6 REAL DEFAULT 0.0
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO app_data (id) VALUES (1)")
    conn.commit()
    conn.close()


init_db()


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


class EstadoReq(BaseModel):
    estado: Literal[0, 1, 2]


class VehiculoReq(BaseModel):
    vehiculo: Optional[Literal["ligero", "pesado"]] = None


class DatosReq(BaseModel):
    dato1: float
    dato2: float
    dato3: float
    dato4: float
    dato5: float
    dato6: float


@app.get("/estado")
def get_estado():
    conn = get_db()
    row = conn.execute("SELECT estado_a FROM app_data WHERE id=1").fetchone()
    conn.close()
    return {"estado_a": row["estado_a"]}


@app.post("/estado")
def set_estado(req: EstadoReq):
    conn = get_db()
    conn.execute("UPDATE app_data SET estado_a = ? WHERE id=1", (req.estado,))
    conn.commit()
    conn.close()
    return {"mensaje": "Estado actualizado", "estado_a": req.estado}


@app.get("/vehiculo")
def get_vehiculo():
    conn = get_db()
    row = conn.execute("SELECT vehiculo_actual FROM app_data WHERE id=1").fetchone()
    conn.close()
    return {"vehiculo_actual": row["vehiculo_actual"]}


@app.post("/vehiculo")
def set_vehiculo(req: VehiculoReq):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE app_data SET vehiculo_actual = ? WHERE id=1", (req.vehiculo,)
    )

    if req.vehiculo == "ligero":
        cursor.execute(
            "UPDATE app_data SET total_vehiculos = total_vehiculos + 1, total_ligeros = total_ligeros + 1 WHERE id=1"
        )
    elif req.vehiculo == "pesado":
        cursor.execute(
            "UPDATE app_data SET total_vehiculos = total_vehiculos + 1, total_pesados = total_pesados + 1 WHERE id=1"
        )

    conn.commit()
    conn.close()
    return {
        "mensaje": "Vehículo y analíticas actualizados",
        "vehiculo_actual": req.vehiculo,
    }


@app.get("/analiticas")
def get_analiticas():
    conn = get_db()
    row = conn.execute(
        "SELECT total_vehiculos, total_ligeros, total_pesados FROM app_data WHERE id=1"
    ).fetchone()
    conn.close()
    return dict(row)


@app.get("/datos")
def get_datos():
    conn = get_db()
    row = conn.execute(
        "SELECT dato1, dato2, dato3, dato4, dato5, dato6 FROM app_data WHERE id=1"
    ).fetchone()
    conn.close()
    return dict(row)


@app.post("/datos")
def set_datos(req: DatosReq):
    conn = get_db()
    conn.execute(
        """
        UPDATE app_data
        SET dato1=?, dato2=?, dato3=?, dato4=?, dato5=?, dato6=?
        WHERE id=1
    """,
        (req.dato1, req.dato2, req.dato3, req.dato4, req.dato5, req.dato6),
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Datos actualizados correctamente"}
