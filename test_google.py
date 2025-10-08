from selenium import webdriver
from selenium.webdriver.common.by import By

def test_busca_google():
    # abre o navegador
    driver = webdriver.Chrome()

    # acessa o Google
    driver.get("https://www.google.com")

    # digita no campo de pesquisa
    campo = driver.find_element(By.NAME, "q")
    campo.send_keys("Botafogo")
    campo.submit()

    # valida se a página trouxe resultados
    assert "Botafogo" in driver.title

    driver.quit()
