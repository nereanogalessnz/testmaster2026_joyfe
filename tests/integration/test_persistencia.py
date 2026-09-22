import sqlite3


def test_producto_se_guarda_realmente_en_sqlite(client, auth_headers, db_path):
    respuesta = client.post(
        "/productos",
        json={"nombre": "Monitor", "precio": 149.99, "stock": 3},
        headers=auth_headers,
    )
    assert respuesta.status_code == 201

    conexion = sqlite3.connect(db_path)
    fila = conexion.execute(
        "SELECT nombre, precio, stock FROM productos WHERE nombre = ?", ("Monitor",)
    ).fetchone()
    conexion.close()

    assert fila == ("Monitor", 149.99, 3)


def test_cliente_se_guarda_realmente_en_sqlite(client, auth_headers, db_path):
    respuesta = client.post(
        "/clientes",
        json={"nombre": "Carlos", "email": "carlos@example.com", "telefono": "611111111"},
        headers=auth_headers,
    )
    assert respuesta.status_code == 201

    conexion = sqlite3.connect(db_path)
    fila = conexion.execute(
        "SELECT nombre, email, telefono FROM clientes WHERE email = ?", ("carlos@example.com",)
    ).fetchone()
    conexion.close()

    assert fila == ("Carlos", "carlos@example.com", "611111111")


def test_usuario_y_token_persisten_en_sqlite(client, usuario, db_path):
    assert client.post("/registro", json=usuario).status_code == 201
    login = client.post("/login", json=usuario)
    assert login.status_code == 200
    token = login.get_json()["token"]

    conexion = sqlite3.connect(db_path)
    usuario_db = conexion.execute("SELECT username FROM usuarios WHERE username = ?", (usuario["username"],)).fetchone()
    token_db = conexion.execute("SELECT username FROM tokens WHERE token = ?", (token,)).fetchone()
    conexion.close()

    assert usuario_db == (usuario["username"],)
    assert token_db == (usuario["username"],)
