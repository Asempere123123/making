import sqlite3
from datetime import datetime
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

BOUNDARY_DATO1 = 200.0
BOUNDARY_DATO5_6 = 500.0

last_sensor_state: Optional[str] = None


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
            lunes INTEGER DEFAULT 0,
            martes INTEGER DEFAULT 0,
            miercoles INTEGER DEFAULT 0,
            jueves INTEGER DEFAULT 0,
            viernes INTEGER DEFAULT 0,
            sabado INTEGER DEFAULT 0,
            domingo INTEGER DEFAULT 0,
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

    # Determine day of the week (0 = Monday, 6 = Sunday)
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    dia_actual = dias[datetime.now().weekday()]

    if req.vehiculo == "ligero":
        cursor.execute(f"""
            UPDATE app_data
            SET total_vehiculos = total_vehiculos + 1,
                total_ligeros = total_ligeros + 1,
                {dia_actual} = {dia_actual} + 1
            WHERE id=1
        """)
    elif req.vehiculo == "pesado":
        cursor.execute(f"""
            UPDATE app_data
            SET total_vehiculos = total_vehiculos + 1,
                total_pesados = total_pesados + 1,
                {dia_actual} = {dia_actual} + 1
            WHERE id=1
        """)

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


@app.get("/semana")
def get_semana():
    conn = get_db()
    row = conn.execute(
        "SELECT lunes, martes, miercoles, jueves, viernes, sabado, domingo FROM app_data WHERE id=1"
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
    global last_sensor_state
    conn = get_db()

    current_data = conn.execute(
        "SELECT dato1, dato2, dato3, dato4, dato5, dato6 FROM app_data WHERE id=1"
    ).fetchone()

    final_dato1 = req.dato1 if req.dato1 != 0.0 else current_data["dato1"]
    final_dato2 = req.dato2 if req.dato2 != 0.0 else current_data["dato2"]
    final_dato3 = req.dato3 if req.dato3 != 0.0 else current_data["dato3"]
    final_dato4 = req.dato4 if req.dato4 != 0.0 else current_data["dato4"]
    final_dato5 = req.dato5 if req.dato5 != 0.0 else current_data["dato5"]
    final_dato6 = req.dato6 if req.dato6 != 0.0 else current_data["dato6"]

    conn.execute(
        """
        UPDATE app_data
        SET dato1=?, dato2=?, dato3=?, dato4=?, dato5=?, dato6=?
        WHERE id=1
        """,
        (final_dato1, final_dato2, final_dato3, final_dato4, final_dato5, final_dato6),
    )
    conn.commit()
    conn.close()

    current_condition = last_sensor_state
    if final_dato1 > BOUNDARY_DATO1:
        current_condition = "none"
    elif final_dato5 < BOUNDARY_DATO5_6 and final_dato6 < BOUNDARY_DATO5_6:
        current_condition = "pesado"
    else:
        current_condition = "ligero"

    if current_condition != last_sensor_state:
        if current_condition == "none":
            set_vehiculo(VehiculoReq(vehiculo=None))
        elif current_condition == "ligero":
            set_vehiculo(VehiculoReq(vehiculo="ligero"))
        elif current_condition == "pesado":
            set_vehiculo(VehiculoReq(vehiculo="pesado"))

        last_sensor_state = current_condition

    return {
        "mensaje": "Datos actualizados correctamente",
        "estado_detectado": last_sensor_state,
    }
