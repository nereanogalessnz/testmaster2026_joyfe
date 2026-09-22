import pytest
from app import validar_registro, validar_producto, validar_cliente


@pytest.mark.parametrize("datos", [
    {"username": "ana", "password": "1234"},
    {"username": "usuario", "password": "clave-segura"},
])
def test_validar_registro_correcto(datos):
    assert validar_registro(datos) is None


@pytest.mark.parametrize("datos, error", [
    (None, "Cuerpo de la peticion invalido"),
    ({}, "El campo username es obligatorio"),
    ({"username": "ana"}, "El campo password debe tener al menos 4 caracteres"),
    ({"username": "ana", "password": "123"}, "El campo password debe tener al menos 4 caracteres"),
])
def test_validar_registro_incorrecto(datos, error):
    assert validar_registro(datos) == error


def test_validar_producto_correcto():
    assert validar_producto({"nombre": "Teclado", "precio": 19.99, "stock": 10}) is None
    assert validar_producto({"nombre": "Gratis", "precio": 0, "stock": 0}) is None


@pytest.mark.parametrize("datos, error", [
    (None, "Cuerpo de la peticion invalido"),
    ({"precio": 10, "stock": 1}, "El campo nombre es obligatorio"),
    ({"nombre": "X", "precio": -1, "stock": 1}, "El campo precio debe ser un numero >= 0"),
    ({"nombre": "X", "precio": True, "stock": 1}, "El campo precio debe ser un numero >= 0"),
    ({"nombre": "X", "precio": 1, "stock": -1}, "El campo stock debe ser un entero >= 0"),
    ({"nombre": "X", "precio": 1, "stock": 1.5}, "El campo stock debe ser un entero >= 0"),
])
def test_validar_producto_incorrecto(datos, error):
    assert validar_producto(datos) == error


def test_validar_cliente_correcto():
    assert validar_cliente({"nombre": "Ana", "email": "ana@example.com"}) is None


@pytest.mark.parametrize("datos, error", [
    (None, "Cuerpo de la peticion invalido"),
    ({"email": "ana@example.com"}, "El campo nombre es obligatorio"),
    ({"nombre": "Ana", "email": "correo-invalido"}, "El campo email no es valido"),
    ({"nombre": "Ana", "email": ""}, "El campo email no es valido"),
])
def test_validar_cliente_incorrecto(datos, error):
    assert validar_cliente(datos) == error
