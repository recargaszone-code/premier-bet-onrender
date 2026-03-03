import os
import time
import threading
import re
import requests
from flask import Flask, jsonify

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# ========================= CONFIG =========================
TELEGRAM_TOKEN = "8742776802:AAHSzD1qTwCqMEOdoW9_pT2l5GfmMBWUZQY"
TELEGRAM_CHAT_ID = "7427648935"
LOGIN = "857789345"
PASSWORD = "max123ZICO"
URL = "https://www.premierbet.co.mz/virtuals/game/aviator-291195"

historico = []

def enviar_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=15
        )
    except:
        pass

# ========================= SCRAPER ESTÁVEL =========================
def iniciar_scraper():
    global historico
    while True:
        driver = None
        try:
            enviar_telegram("🟢 Iniciando scraper ESTÁVEL no Railway...")

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1280,720")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            wait = WebDriverWait(driver, 60)

            driver.get(URL)
            enviar_telegram("🌐 Página aberta - aguardando 25s")
            time.sleep(25)

            # Mais Tarde
            try:
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.kumulos-action-button.kumulos-action-button-cancel")))
                btn.click()
                enviar_telegram("✅ Mais Tarde clicado")
            except TimeoutException:
                enviar_telegram("⚠️ Mais Tarde não apareceu")
            time.sleep(25)

            # LOGIN
            enviar_telegram("🔑 Tentando login...")
            login_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))
            driver.execute_script("arguments[0].value = '';", login_input)
            login_input.send_keys(LOGIN)
            enviar_telegram("📌 Número preenchido")
            time.sleep(20)

            pwd = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            driver.execute_script("arguments[0].value = '';", pwd)
            pwd.send_keys(PASSWORD)
            enviar_telegram("📌 Senha preenchida")
            time.sleep(20)

            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.form-button.form-button--primary")))
            btn.click()
            enviar_telegram("✅ 6. Login enviado!")
            time.sleep(35)

            # IFRAME
            enviar_telegram("🎯 Aguardando iframe...")
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.casino-game-launch-iframe__frame")))
            driver.switch_to.frame(iframe)
            enviar_telegram("✅ 7. Entrou no iframe!")
            time.sleep(25)

            enviar_telegram("🚀 Monitoramento iniciado (a cada 25s)")

            # LOOP HISTÓRICO
            while True:
                wrapper = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div._itemsWrapper_7l84e_35")))
                buttons = wrapper.find_elements(By.CSS_SELECTOR, "button._container_12jzl_1 span._container_1p5jb_1")

                novos = [float(re.search(r'(\d+\.?\d*)', span.text.strip()).group(1))
                         for span in buttons if re.search(r'(\d+\.?\d*)', span.text.strip())]

                if novos and (not historico or novos != historico):
                    historico = novos
                    lista_str = ", ".join(f"{v:.2f}x" for v in historico[-30:])
                    msg = f"""*📊 Histórico Aviator Atualizado*

[{lista_str}]

Total: **{len(historico)}** | Último: **{historico[-1]:.2f}x**"""
                    enviar_telegram(msg)

                time.sleep(25)

        except TimeoutException:
            enviar_telegram("⏳ Timeout - tentando novamente...")
            time.sleep(15)
        except Exception as e:
            enviar_telegram(f"🔥 ERRO: {type(e).__name__} → reiniciando em 20s")
            time.sleep(20)
        finally:
            try:
                if driver:
                    driver.quit()
            except:
                pass

# ========================= API =========================
@app.route("/api/history")
def get_history(): return jsonify(historico)
@app.route("/api/last")
def get_last(): return jsonify(historico[-1] if historico else None)
@app.route("/")
def home(): return "✅ Aviator Railway ESTÁVEL rodando!"

if __name__ == "__main__":
    threading.Thread(target=iniciar_scraper, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
