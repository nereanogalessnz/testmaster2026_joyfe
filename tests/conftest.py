import pytest
from app import crear_app


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def app(db_path):
    app = crear_app(str(db_path))
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuario():
    return {"username": "nerea", "password": "1234"}


@pytest.fixture
def token(client, usuario):
    respuesta = client.post("/registro", json=usuario)
    assert respuesta.status_code == 201
    respuesta = client.post("/login", json=usuario)
    assert respuesta.status_code == 200
    return respuesta.get_json()["token"]


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
