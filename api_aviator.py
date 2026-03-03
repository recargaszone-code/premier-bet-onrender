import os
import time
import threading
import re
import requests
from flask import Flask, jsonify

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

# ========================= SCRAPER ANTI-CLOUDFRONT =========================
def iniciar_scraper():
    global historico
    while True:
        driver = None
        try:
            enviar_telegram("🟢 Iniciando Stealth Anti-CloudFront (25s por passo)...")

            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-setuid-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-logging")
            options.add_argument("--log-level=3")
            options.add_argument("--window-size=1280,720")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36")

            # === STEALTH MÁXIMO CONTRA CLOUDFRONT ===
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")

            driver = uc.Chrome(version_main=145, options=options)

            # Esconde que é Selenium
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            wait = WebDriverWait(driver, 45)

            # PASSO 1 - ABRIR PÁGINA
            driver.get(URL)
            enviar_telegram("🌐 Página aberta")
            time.sleep(25)

            # PASSO 2 - MAIS TARDE
            try:
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.kumulos-action-button.kumulos-action-button-cancel")))
                btn.click()
                enviar_telegram("✅ Mais Tarde clicado")
            except:
                pass
            time.sleep(25)

            # PASSO 3 - LOGIN (bem espaçado)
            enviar_telegram("🔑 Iniciando login...")
            time.sleep(10)

            login_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))
            driver.execute_script("arguments[0].value = '';", login_input)
            login_input.send_keys(LOGIN)
            time.sleep(15)

            pwd = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            driver.execute_script("arguments[0].value = '';", pwd)
            pwd.send_keys(PASSWORD)
            time.sleep(15)

            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.form-button.form-button--primary")))
            btn.click()
            enviar_telegram("✅ Login enviado")
            time.sleep(30)   # tempo crítico pro jogo carregar

            # PASSO 4 - IFRAME (sem loop agressivo)
            enviar_telegram("🎯 Aguardando iframe...")
            time.sleep(25)
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.casino-game-launch-iframe__frame")))
            driver.switch_to.frame(iframe)
            enviar_telegram("✅ 7. Entrou no iframe!")
            time.sleep(25)

            enviar_telegram("🚀 Monitoramento iniciado (a cada 25s)")

            # LOOP HISTÓRICO (25 SEGUNDOS)
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

        except Exception as e:
            enviar_telegram(f"⚠️ Erro: {type(e).__name__} (reiniciando em 20s)")
        finally:
            try:
                if driver:
                    driver.quit()
            except:
                pass
            time.sleep(20)

# ========================= API =========================
@app.route("/api/history")
def get_history(): return jsonify(historico)
@app.route("/api/last")
def get_last(): return jsonify(historico[-1] if historico else None)
@app.route("/")
def home(): return "✅ Aviator Railway + Anti-CloudFront rodando!"

if __name__ == "__main__":
    threading.Thread(target=iniciar_scraper, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
