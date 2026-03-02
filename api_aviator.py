from flask import Flask, jsonify
import threading
import time
import re
import random
import requests
import os

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================== CONFIG ==================
LOGIN = "857789345"
PASSWORD = "max123ZICO"

TELEGRAM_BOT_TOKEN = "SEU_BOT_TOKEN"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID"

URL = "https://www.premierbet.co.mz/virtuals/game/aviator-291195"

# ============================================

app = Flask(__name__)
historico = []
driver = None

# ================== TELEGRAM ==================
def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Erro Telegram:", e)


# ================== CRIAR DRIVER ==================
def criar_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1366,768")
    options.binary_location = "/usr/bin/chromium"

    return uc.Chrome(options=options)


# ================== SCRAPER ==================
def iniciar_scraper():
    global historico, driver

    while True:
        try:
            print("Iniciando navegador...")
            driver = criar_driver()
            wait = WebDriverWait(driver, 60)

            print("Abrindo Aviator...")
            driver.get(URL)
            time.sleep(15)

            # ================= LOGIN =================
            try:
                print("Fazendo login...")
                login_input = wait.until(EC.element_to_be_clickable((By.NAME, "login")))
                login_input.clear()
                login_input.send_keys(LOGIN)

                pwd = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
                pwd.clear()
                pwd.send_keys(PASSWORD)

                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.form-button.form-button--primary")))
                btn.click()

                print("Login enviado, aguardando carregar jogo...")
                time.sleep(25)

            except Exception as e:
                print("Login não necessário ou erro:", e)
                time.sleep(20)

            # ================= IFRAME =================
            print("Entrando no iframe do jogo...")
            iframe = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe.casino-game-launch-iframe__frame")
            ))
            driver.switch_to.frame(iframe)
            print("Iframe conectado! Scraper ativo.")

            ultimo_enviado = None

            while True:
                try:
                    items_wrapper = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div._itemsWrapper_7l84e_35"))
                    )

                    buttons = items_wrapper.find_elements(
                        By.CSS_SELECTOR,
                        "button._container_12jzl_1 span._container_1p5jb_1"
                    )

                    novos = []
                    for span in buttons:
                        txt = span.text.strip()
                        if txt:
                            match = re.search(r'(\d+\.?\d*)', txt)
                            if match:
                                novos.append(float(match.group(1)))

                    if novos:
                        historico = novos
                        ultimo = historico[-1]
                        print(f"[SCRAPER] Último: {ultimo} | Total: {len(historico)}")

                        if ultimo_enviado != ultimo:
                            lista_str = ", ".join(f"{v:.2f}" for v in historico[-20:])
                            msg = (
                                f"*Aviator Histórico Atualizado*\n\n"
                                f"[{lista_str}]\n\n"
                                f"Último: *{ultimo:.2f}x*\n"
                                f"Total: *{len(historico)}*"
                            )
                            enviar_telegram(msg)
                            ultimo_enviado = ultimo

                except Exception as e:
                    print("Erro loop scraping:", e)
                    break

                time.sleep(random.uniform(6, 10))

        except Exception as e:
            print("Erro geral, reiniciando driver:", e)

        time.sleep(10)


# ================== API ==================
@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify({
        "history": historico[-50:],
        "last": historico[-1] if historico else None,
        "total": len(historico)
    })


@app.route("/api/last", methods=["GET"])
def get_last():
    return jsonify({
        "last": historico[-1] if historico else None
    })


@app.route("/api/full", methods=["GET"])
def get_full():
    return jsonify({
        "history": historico
    })


# ================== MAIN ==================
if __name__ == "__main__":
    t = threading.Thread(target=iniciar_scraper)
    t.daemon = True
    t.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)