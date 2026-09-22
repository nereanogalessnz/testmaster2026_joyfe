import sqlite3
from app import init_db


def test_init_db_crea_fichero_y_tablas(tmp_path):
    ruta = tmp_path / "unidad.db"
    init_db(str(ruta))
    assert ruta.exists()

    conexion = sqlite3.connect(ruta)
    tablas = {
        fila[0]
        for fila in conexion.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conexion.close()

    assert {"usuarios", "tokens", "productos", "clientes"}.issubset(tablas)


def test_init_db_es_idempotente(tmp_path):
    ruta = tmp_path / "unidad.db"
    init_db(str(ruta))
    init_db(str(ruta))

    conexion = sqlite3.connect(ruta)
    cantidad = conexion.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('usuarios','tokens','productos','clientes')"
    ).fetchone()[0]
    conexion.close()
    assert cantidad == 4


def test_username_tiene_restriccion_unique(tmp_path):
    ruta = tmp_path / "unidad.db"
    init_db(str(ruta))
    conexion = sqlite3.connect(ruta)
    conexion.execute("INSERT INTO usuarios(username, password_hash) VALUES (?, ?)", ("ana", "hash"))
    conexion.commit()

    try:
        conexion.execute("INSERT INTO usuarios(username, password_hash) VALUES (?, ?)", ("ana", "otro"))
        conexion.commit()
        assert False, "La columna username deberia ser UNIQUE"
    except sqlite3.IntegrityError:
        pass
    finally:
        conexion.close()
