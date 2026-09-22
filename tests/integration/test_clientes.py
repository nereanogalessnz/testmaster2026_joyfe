def test_crud_completo_clientes(client, auth_headers):
    nuevo = {"nombre": "Ana Garcia", "email": "ana@example.com", "telefono": "600123123"}
    respuesta = client.post("/clientes", json=nuevo, headers=auth_headers)
    assert respuesta.status_code == 201
    cliente = respuesta.get_json()
    cliente_id = cliente["id"]
    assert cliente["email"] == "ana@example.com"

    respuesta = client.get("/clientes", headers=auth_headers)
    assert respuesta.status_code == 200
    assert len(respuesta.get_json()) == 1

    respuesta = client.get(f"/clientes/{cliente_id}", headers=auth_headers)
    assert respuesta.status_code == 200
    assert respuesta.get_json()["nombre"] == "Ana Garcia"

    actualizado = {"nombre": "Ana Lopez", "email": "ana.lopez@example.com"}
    respuesta = client.put(f"/clientes/{cliente_id}", json=actualizado, headers=auth_headers)
    assert respuesta.status_code == 200
    assert respuesta.get_json()["nombre"] == "Ana Lopez"
    assert respuesta.get_json()["telefono"] == ""

    respuesta = client.delete(f"/clientes/{cliente_id}", headers=auth_headers)
    assert respuesta.status_code == 204
    assert client.get(f"/clientes/{cliente_id}", headers=auth_headers).status_code == 404


def test_cliente_email_invalido(client, auth_headers):
    respuesta = client.post(
        "/clientes",
        json={"nombre": "Ana", "email": "correo-invalido"},
        headers=auth_headers,
    )
    assert respuesta.status_code == 400


def test_cliente_telefono_opcional(client, auth_headers):
    respuesta = client.post(
        "/clientes",
        json={"nombre": "Luis", "email": "luis@example.com"},
        headers=auth_headers,
    )
    assert respuesta.status_code == 201
    assert respuesta.get_json()["telefono"] == ""


def test_cliente_inexistente(client, auth_headers):
    assert client.get("/clientes/9999", headers=auth_headers).status_code == 404
    assert client.put("/clientes/9999", json={"nombre": "X", "email": "x@x.es"}, headers=auth_headers).status_code == 404
    assert client.delete("/clientes/9999", headers=auth_headers).status_code == 404
