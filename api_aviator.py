import os
import time
import traceback
import requests
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# =========================
# CREDENCIAIS ANTIGAS (TESTE)
# =========================
TELEGRAM_TOKEN = "8742776802:AAHSzD1qTwCqMEOdoW9_pT2l5GfmMBWUZQY"
TELEGRAM_CHAT_ID = "7427648935"

LOGIN = "857789345"
PASSWORD = "max123ZICO"

URL = "https://www.premierbet.co.mz/virtuals/game/aviator-291195"

historico = []

# =========================
# TELEGRAM
# =========================
def enviar_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode":"Markdown"}
        )
    except:
        pass

def enviar_print(driver, legenda="📸 Screenshot"):
    try:
        path = "/tmp/print.png"
        driver.save_screenshot(path)
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            files={"photo": open(path, "rb")},
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": legenda}
        )
    except Exception as e:
        enviar_telegram(f"❌ Erro ao enviar print: {e}")

# =========================
# SCRAPER
# =========================
def iniciar_scraper():
    global historico

    while True:
        driver = None
        try:
            enviar_telegram("🟢 Iniciando navegador Chrome headless...")

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(URL)
            enviar_telegram("🌐 Página aberta!")
            time.sleep(15)
            enviar_print(driver, "📸 Página carregada")

            # LOGIN
            try:
                login_input = driver.find_element(By.NAME, "login")
                login_input.clear()
                login_input.send_keys(LOGIN)

                pwd_input = driver.find_element(By.NAME, "password")
                pwd_input.clear()
                pwd_input.send_keys(PASSWORD)

                btn = driver.find_element(By.CSS_SELECTOR, "button.form-button.form-button--primary")
                btn.click()
                enviar_telegram("✅ Login enviado!")
                time.sleep(25)
            except:
                enviar_telegram("⚠️ Login não necessário ou falhou!")

            # IFRAME
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            enviar_telegram(f"🎯 Iframes encontrados: {len(iframes)}")
            if len(iframes) == 0:
                raise Exception("Nenhum iframe encontrado")
            driver.switch_to.frame(iframes[-1])
            enviar_telegram("✅ Entrou no iframe do Aviator")
            time.sleep(10)
            enviar_print(driver, "🎮 Dentro do iframe")

            # LOOP HISTÓRICO
            ultimo_enviado = None
            while True:
                elementos = driver.find_elements(By.CSS_SELECTOR, "div._itemsWrapper_7l84e_35 span._container_1p5jb_1")
                novos = []
                for el in elementos:
                    txt = el.text.replace("x","").strip()
                    if txt:
                        try:
                            novos.append(float(txt))
                        except:
                            continue

                if novos and novos != historico:
                    historico = novos[:50]
                    enviar_telegram(f"📊 Histórico atualizado (últimos 10): {historico[:10]}")
                    enviar_print(driver, "📸 Histórico atualizado")

                time.sleep(6)

        except Exception as e:
            erro = traceback.format_exc()
            enviar_telegram(f"🔥 ERRO NO SCRAPER:\n{erro}")
            time.sleep(10)

        finally:
            try:
                driver.quit()
            except:
                pass
            enviar_telegram("🔄 Reiniciando scraper em 10s...")
            time.sleep(10)

# =========================
# API
# =========================
@app.route("/api/history")
def get_history():
    return jsonify(historico)

@app.route("/api/last")
def get_last():
    return jsonify(historico[-1] if historico else None)

@app.route("/")
def home():
    return "Scraper Aviator rodando!"

# =========================
# THREAD SCRAPER
# =========================
import threading
threading.Thread(target=iniciar_scraper, daemon=True).start()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
