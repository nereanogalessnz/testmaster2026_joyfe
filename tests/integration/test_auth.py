def test_registro_correcto(client):
    respuesta = client.post("/registro", json={"username": "ana", "password": "1234"})
    assert respuesta.status_code == 201
    assert respuesta.get_json()["mensaje"] == "Usuario creado correctamente"


def test_registro_duplicado(client):
    datos = {"username": "ana", "password": "1234"}
    assert client.post("/registro", json=datos).status_code == 201
    respuesta = client.post("/registro", json=datos)
    assert respuesta.status_code == 409
    assert respuesta.get_json()["error"] == "Ese usuario ya existe"


def test_registro_invalido(client):
    respuesta = client.post("/registro", json={"username": "ana", "password": "123"})
    assert respuesta.status_code == 400


def test_login_correcto(client):
    datos = {"username": "ana", "password": "1234"}
    client.post("/registro", json=datos)
    respuesta = client.post("/login", json=datos)
    assert respuesta.status_code == 200
    assert len(respuesta.get_json()["token"]) == 32


def test_login_incorrecto(client):
    client.post("/registro", json={"username": "ana", "password": "1234"})
    respuesta = client.post("/login", json={"username": "ana", "password": "incorrecta"})
    assert respuesta.status_code == 401


def test_ruta_protegida_sin_token(client):
    respuesta = client.get("/productos")
    assert respuesta.status_code == 401
    assert respuesta.get_json()["error"] == "Falta el token de autenticacion"


def test_ruta_protegida_token_invalido(client):
    respuesta = client.get("/productos", headers={"Authorization": "Bearer inventado"})
    assert respuesta.status_code == 401
    assert respuesta.get_json()["error"] == "Token invalido o caducado"


def test_ruta_protegida_token_valido(client, auth_headers):
    respuesta = client.get("/productos", headers=auth_headers)
    assert respuesta.status_code == 200
