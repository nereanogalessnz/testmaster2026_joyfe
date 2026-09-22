def test_crud_completo_productos(client, auth_headers):
    nuevo = {"nombre": "Teclado", "precio": 19.99, "stock": 10}
    respuesta = client.post("/productos", json=nuevo, headers=auth_headers)
    assert respuesta.status_code == 201
    producto = respuesta.get_json()
    producto_id = producto["id"]
    assert producto["nombre"] == "Teclado"

    respuesta = client.get("/productos", headers=auth_headers)
    assert respuesta.status_code == 200
    assert len(respuesta.get_json()) == 1

    respuesta = client.get(f"/productos/{producto_id}", headers=auth_headers)
    assert respuesta.status_code == 200
    assert respuesta.get_json()["precio"] == 19.99

    actualizado = {"nombre": "Teclado mecanico", "precio": 29.99, "stock": 5}
    respuesta = client.put(f"/productos/{producto_id}", json=actualizado, headers=auth_headers)
    assert respuesta.status_code == 200
    assert respuesta.get_json()["nombre"] == "Teclado mecanico"

    respuesta = client.delete(f"/productos/{producto_id}", headers=auth_headers)
    assert respuesta.status_code == 204

    assert client.get(f"/productos/{producto_id}", headers=auth_headers).status_code == 404


def test_producto_datos_invalidos(client, auth_headers):
    respuesta = client.post(
        "/productos",
        json={"nombre": "Teclado", "precio": -10, "stock": 2},
        headers=auth_headers,
    )
    assert respuesta.status_code == 400


def test_producto_inexistente(client, auth_headers):
    assert client.get("/productos/9999", headers=auth_headers).status_code == 404
    assert client.put("/productos/9999", json={"nombre": "X", "precio": 1, "stock": 1}, headers=auth_headers).status_code == 404
    assert client.delete("/productos/9999", headers=auth_headers).status_code == 404
