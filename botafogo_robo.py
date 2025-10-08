from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options # Importação Adicionada
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================================================================
# 🚨 PASSO 1: SUAS CREDENCIAIS E LOCALIZADORES
# =========================================================================
SEU_EMAIL = "vitinhuw@gmail.com" # <--- SUBSTITUA PELO SEU EMAIL
SUA_SENHA = "N@t199585tolo"          # <--- SUBSTITUA PELA SUA SENHA

LOCALIZADOR_EMAIL = "input[placeholder*='exemplo@mail.com']"
LOCALIZADOR_SENHA = "input[placeholder*='Adicione sua senha']"
# =========================================================================

# --- CONFIGURAÇÃO ---
CHROME_DRIVER_PATH = r"C:\Users\valbuquerque\Desktop\meu_primeiro_teste\chromedriver.exe" 
service = Service(CHROME_DRIVER_PATH)

# Configura as opções do Chrome
chrome_options = Options()
# Mantém o navegador aberto após o script terminar:
chrome_options.add_experimental_option("detach", True) 

# Inicializa o Driver
print("1. Inicializando o navegador...")
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 45) 

LOGIN_URL = "https://store.botafogo.com.br/login?returnUrl=%2F"

try:
    # 2. ACESSO DIRETO À PÁGINA DE LOGIN
    print(f"2. Acessando o site de login: {LOGIN_URL}")
    driver.get(LOGIN_URL)
    
    # 3. PREENCHE OS CAMPOS E SUBMETE O FORMULÁRIO COM ENTER
    print("3. Preenchendo campos de email e senha...")
    
    campo_email = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, LOCALIZADOR_EMAIL)) 
    )
    campo_email.send_keys(SEU_EMAIL)
    
    campo_senha = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, LOCALIZADOR_SENHA))
    )
    campo_senha.send_keys(SUA_SENHA)
    
    # Submissão: Simula a tecla ENTER para logar
    print("4. Submetendo formulário com a tecla ENTER...")
    campo_senha.send_keys(Keys.RETURN) 
    
    print("5. Login concluído. O navegador permanecerá aberto.")

except Exception as e:
    print(f"Ocorreu um erro durante a automação: {e}")
    
# O script Python termina aqui. O navegador permanece aberto devido à opção 'detach'.
print("\n6. Script Python finalizado. O navegador Chrome permanecerá aberto. Feche a janela do navegador manualmente.")

# A linha 'time.sleep(3600)' foi removida!