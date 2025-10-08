import requests

def test_buscar_usuario():
    # envia requisição GET para a API
    resposta = requests.get("https://jsonplaceholder.typicode.com/users/1")

    # valida se a resposta foi sucesso (status code 200)
    assert resposta.status_code == 200

    # converte resposta para JSON (dicionário Python)
    dados = resposta.json()

    # valida alguns campos
    assert dados["id"] == 1
    assert "Leanne Graham" in dados["name"]