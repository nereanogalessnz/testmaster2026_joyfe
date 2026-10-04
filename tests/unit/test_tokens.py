from app import generar_token


def test_generar_token_devuelve_cadena_hexadecimal():
    token = generar_token()
    assert isinstance(token, str)
    assert len(token) == 32
    int(token, 16)


def test_generar_token_genera_valores_distintos():
    tokens = {generar_token() for _ in range(20)}
    assert len(tokens) == 20
