import os
import sys
import tempfile

import pytest

# Añadir la raíz del proyecto al path de Python
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

from app import crear_app


@pytest.fixture
def client():
    # Creamos una base de datos temporal para cada test
    db_fd, db_path = tempfile.mkstemp()

    app = crear_app(db_path)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    # Eliminamos la base de datos temporal al terminar
    os.close(db_fd)
    os.unlink(db_path)


def test_registro_usuario(client):
    respuesta = client.post(
        "/registro",
        json={
            "username": "nerea_test",
            "password": "Password123"
        }
    )

    assert respuesta.status_code == 201

def test_registro_usuario_duplicado(client):
    datos = {
        "username": "nerea_test",
        "password": "Password123"
    }

    # Primer registro
    respuesta1 = client.post("/registro", json=datos)
    assert respuesta1.status_code == 201

    # Intentamos registrar el mismo usuario otra vez
    respuesta2 = client.post("/registro", json=datos)

    assert respuesta2.status_code == 409
    assert respuesta2.get_json()["error"] == "Ese usuario ya existe"

def test_login_correcto(client):
    # Primero registramos al usuario
    datos = {
        "username": "nerea_test",
        "password": "Password123"
    }

    registro = client.post("/registro", json=datos)
    assert registro.status_code == 201

    # Después iniciamos sesión con ese usuario
    login = client.post("/login", json=datos)

    assert login.status_code == 200

    respuesta = login.get_json()
    assert "token" in respuesta

def test_login_password_incorrecta(client):
    # Primero registramos al usuario
    datos_registro = {
        "username": "nerea_test",
        "password": "Password123"
    }

    registro = client.post("/registro", json=datos_registro)
    assert registro.status_code == 201

    # Intentamos iniciar sesión con contraseña incorrecta
    datos_login = {
        "username": "nerea_test",
        "password": "PasswordIncorrecta"
    }

    login = client.post("/login", json=datos_login)

    assert login.status_code == 401

def test_crear_producto(client):
    # 1. Registramos un usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    registro = client.post("/registro", json=datos_usuario)
    assert registro.status_code == 201

    # 2. Iniciamos sesión para obtener el token
    login = client.post("/login", json=datos_usuario)
    assert login.status_code == 200

    token = login.get_json()["token"]

    # 3. Creamos un producto usando el token
    producto = {
        "nombre": "Teclado",
        "precio": 29.99,
        "stock": 10
    }

    respuesta = client.post(
        "/productos",
        json=producto,
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. Comprobamos el resultado
    assert respuesta.status_code == 201

    datos = respuesta.get_json()
    assert datos["nombre"] == "Teclado"
    assert datos["precio"] == 29.99
    assert datos["stock"] == 10

def test_obtener_producto(client):
    # 1. Registramos un usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Iniciamos sesión y obtenemos el token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Creamos un producto
    producto = {
        "nombre": "Raton",
        "precio": 19.99,
        "stock": 5
    }

    creacion = client.post(
        "/productos",
        json=producto,
        headers=headers
    )

    assert creacion.status_code == 201

    # Guardamos el ID que le ha asignado la base de datos
    id_producto = creacion.get_json()["id"]

    # 4. Consultamos ese producto
    respuesta = client.get(
        f"/productos/{id_producto}",
        headers=headers
    )

    # 5. Comprobamos los datos
    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["id"] == id_producto
    assert datos["nombre"] == "Raton"
    assert datos["precio"] == 19.99
    assert datos["stock"] == 5

def test_producto_no_encontrado(client):
    # 1. Registramos un usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Iniciamos sesión y obtenemos el token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    # 3. Intentamos consultar un producto que no existe
    respuesta = client.get(
        "/productos/9999",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. Comprobamos la respuesta
    assert respuesta.status_code == 404
    assert respuesta.get_json()["error"] == "Producto no encontrado"

def test_actualizar_producto(client):
    # 1. Registramos usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Login y token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Creamos un producto
    producto = {
        "nombre": "Teclado",
        "precio": 29.99,
        "stock": 10
    }

    creacion = client.post(
        "/productos",
        json=producto,
        headers=headers
    )

    id_producto = creacion.get_json()["id"]

    # 4. Modificamos el producto
    producto_actualizado = {
        "nombre": "Teclado Gaming",
        "precio": 49.99,
        "stock": 15
    }

    respuesta = client.put(
        f"/productos/{id_producto}",
        json=producto_actualizado,
        headers=headers
    )

    assert respuesta.status_code == 200
    # 5. Consultamos de nuevo el producto
    consulta = client.get(
        f"/productos/{id_producto}",
        headers=headers
    )

    assert consulta.status_code == 200

    datos = consulta.get_json()

    # 6. Comprobamos que los cambios se guardaron
    assert datos["nombre"] == "Teclado Gaming"
    assert datos["precio"] == 49.99
    assert datos["stock"] == 15

def test_eliminar_producto(client):
    # 1. Registramos usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Login y obtenemos token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Creamos un producto
    producto = {
        "nombre": "Monitor",
        "precio": 199.99,
        "stock": 4
    }

    creacion = client.post(
        "/productos",
        json=producto,
        headers=headers
    )

    assert creacion.status_code == 201

    id_producto = creacion.get_json()["id"]

    # 4. Eliminamos el producto
    eliminacion = client.delete(
        f"/productos/{id_producto}",
        headers=headers
    )

    assert eliminacion.status_code == 204

    # 5. Intentamos consultar el producto eliminado
    consulta = client.get(
        f"/productos/{id_producto}",
        headers=headers
    )

    # Ya no debe existir
    assert consulta.status_code == 404
    assert consulta.get_json()["error"] == "Producto no encontrado"

def test_crear_cliente(client):
    # 1. Registramos usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Login y obtenemos token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Creamos un cliente
    cliente = {
        "nombre": "Nerea Nogales",
        "email": "nerea@ejemplo.com",
        "telefono": "600123123"
    }

    respuesta = client.post(
        "/clientes",
        json=cliente,
        headers=headers
    )

    # 4. Comprobamos la respuesta
    assert respuesta.status_code == 201

    datos = respuesta.get_json()

    assert datos["nombre"] == "Nerea Nogales"
    assert datos["email"] == "nerea@ejemplo.com"
    assert datos["telefono"] == "600123123"

def test_obtener_cliente(client):
    # 1. Registramos usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Login y obtenemos token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Creamos un cliente
    cliente = {
        "nombre": "Ana Garcia",
        "email": "ana@ejemplo.com",
        "telefono": "611222333"
    }

    creacion = client.post(
        "/clientes",
        json=cliente,
        headers=headers
    )

    assert creacion.status_code == 201

    id_cliente = creacion.get_json()["id"]

    # 4. Consultamos el cliente creado
    respuesta = client.get(
        f"/clientes/{id_cliente}",
        headers=headers
    )

    # 5. Comprobamos los datos
    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["id"] == id_cliente
    assert datos["nombre"] == "Ana Garcia"
    assert datos["email"] == "ana@ejemplo.com"
    assert datos["telefono"] == "611222333"

def test_actualizar_cliente(client):
    # 1. Registramos usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Login y token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Creamos un cliente
    cliente = {
        "nombre": "Carlos Lopez",
        "email": "carlos@ejemplo.com",
        "telefono": "622333444"
    }

    creacion = client.post(
        "/clientes",
        json=cliente,
        headers=headers
    )

    assert creacion.status_code == 201

    id_cliente = creacion.get_json()["id"]

    # 4. Actualizamos el cliente
    cliente_actualizado = {
        "nombre": "Carlos Lopez Garcia",
        "email": "carlos.nuevo@ejemplo.com",
        "telefono": "633444555"
    }

    respuesta = client.put(
        f"/clientes/{id_cliente}",
        json=cliente_actualizado,
        headers=headers
    )

    assert respuesta.status_code == 200

    # 5. Consultamos de nuevo el cliente
    consulta = client.get(
        f"/clientes/{id_cliente}",
        headers=headers
    )

    assert consulta.status_code == 200

    datos = consulta.get_json()

    # 6. Comprobamos que los cambios se guardaron
    assert datos["nombre"] == "Carlos Lopez Garcia"
    assert datos["email"] == "carlos.nuevo@ejemplo.com"
    assert datos["telefono"] == "633444555"

def test_eliminar_cliente(client):
    # 1. Registramos usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Login y token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Creamos un cliente
    cliente = {
        "nombre": "Laura Martin",
        "email": "laura@ejemplo.com",
        "telefono": "644555666"
    }

    creacion = client.post(
        "/clientes",
        json=cliente,
        headers=headers
    )

    assert creacion.status_code == 201

    id_cliente = creacion.get_json()["id"]

    # 4. Eliminamos el cliente
    eliminacion = client.delete(
        f"/clientes/{id_cliente}",
        headers=headers
    )

    assert eliminacion.status_code == 204

    # 5. Intentamos consultar el cliente eliminado
    consulta = client.get(
        f"/clientes/{id_cliente}",
        headers=headers
    )

    assert consulta.status_code == 404
    assert consulta.get_json()["error"] == "Cliente no encontrado"

def test_acceso_productos_sin_token(client):
    # Intentamos acceder a productos sin iniciar sesión
    respuesta = client.get("/productos")

    # Debe rechazar el acceso
    assert respuesta.status_code == 401
    assert respuesta.get_json()["error"] == "Falta el token de autenticacion"

def test_acceso_con_token_invalido(client):
    # Intentamos acceder usando un token inventado
    headers = {
        "Authorization": "Bearer token_invalido_12345"
    }

    respuesta = client.get(
        "/productos",
        headers=headers
    )

    # Debe rechazar el token
    assert respuesta.status_code == 401
    assert respuesta.get_json()["error"] == "Token invalido o caducado"

def test_crear_producto_precio_invalido(client):
    # 1. Registramos usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Login y token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Intentamos crear un producto con precio negativo
    producto = {
        "nombre": "Teclado",
        "precio": -10,
        "stock": 5
    }

    respuesta = client.post(
        "/productos",
        json=producto,
        headers=headers
    )

    # 4. Debe rechazar los datos
    assert respuesta.status_code == 400
    assert respuesta.get_json()["error"] == "El campo precio debe ser un numero >= 0"

def test_crear_cliente_email_invalido(client):
    # 1. Registramos usuario
    datos_usuario = {
        "username": "nerea_test",
        "password": "Password123"
    }

    client.post("/registro", json=datos_usuario)

    # 2. Login y token
    login = client.post("/login", json=datos_usuario)
    token = login.get_json()["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Intentamos crear un cliente con email incorrecto
    cliente = {
        "nombre": "Laura Martin",
        "email": "correo-invalido",
        "telefono": "644555666"
    }

    respuesta = client.post(
        "/clientes",
        json=cliente,
        headers=headers
    )

    # 4. Debe rechazar los datos
    assert respuesta.status_code == 400
    assert respuesta.get_json()["error"] == "El campo email no es valido"