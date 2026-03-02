import os
import time
import traceback
import threading
import random
import re
import requests
from flask import Flask, jsonify

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException

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
            timeout=10
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
        enviar_telegram(f"❌ Erro print: {e}")

def clicar_mais_tarde(driver):
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.kumulos-action-button.kumulos-action-button-cancel"))
        )
        btn.click()
        time.sleep(2)
    except:
        pass

# ========================= SCRAPER =========================
def iniciar_scraper():
    global historico
    while True:
        driver = None
        try:
            enviar_telegram("🟢 Iniciando undetected Chrome v145...")

            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36")

            # LINHA QUE VOCÊ PEDIU:
            driver = uc.Chrome(version_main=145, options=options)

            wait = WebDriverWait(driver, 45)

            driver.get(URL)
            enviar_telegram("🌐 Página aberta!")
            time.sleep(15)
            enviar_print(driver, "📸 Página inicial carregada")

            clicar_mais_tarde(driver)

            # ==================== REMOVER OVERLAY ====================
            try:
                mask = driver.find_element(By.CSS_SELECTOR, "div.kumulos-background-mask")
                driver.execute_script("arguments[0].style.display = 'none';", mask)
                enviar_telegram("✅ Overlay removido")
            except:
                pass

            # ==================== LOGIN LENTO ====================
            try:
                enviar_telegram("🔑 Tentando login...")
                # Login
                login_input = wait.until(EC.element_to_be_clickable((By.NAME, "login")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_input)
                time.sleep(1.5)
                login_input.click()
                login_input.clear()
                for char in LOGIN:
                    login_input.send_keys(char)
                    time.sleep(0.08)

                # Senha
                pwd = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pwd)
                time.sleep(1.5)
                pwd.click()
                pwd.clear()
                for char in PASSWORD:
                    pwd.send_keys(char)
                    time.sleep(0.08)

                # Botão
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.form-button.form-button--primary")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(1.5)
                try:
                    btn.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", btn)

                enviar_telegram("✅ Login enviado!")
                time.sleep(25)
            except Exception as e:
                enviar_telegram(f"⚠️ Login pulado: {type(e).__name__}")
                time.sleep(25)

            clicar_mais_tarde(driver)

            # ==================== IFRAME ====================
            try:
                iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.casino-game-launch-iframe__frame")))
                driver.switch_to.frame(iframe)
                enviar_telegram("✅ Entrou no iframe específico")
            except:
                # fallback
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    driver.switch_to.frame(iframes[-1])
                    enviar_telegram("✅ Entrou no último iframe (fallback)")
                else:
                    raise Exception("Iframe não encontrado")

            time.sleep(10)
            enviar_print(driver, "🎮 Dentro do jogo")

            # ==================== LOOP HISTÓRICO ====================
            while True:
                clicar_mais_tarde(driver)

                # Captura histórico
                wrapper = WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div._itemsWrapper_7l84e_35"))
                )
                spans = wrapper.find_elements(By.CSS_SELECTOR, "button._container_12jzl_1 span._container_1p5jb_1")

                novos = []
                for span in spans:
                    txt = span.text.strip()
                    if txt:
                        match = re.search(r'(\d+\.?\d*)', txt)
                        if match:
                            novos.append(float(match.group(1)))

                if novos and (not historico or novos != historico):
                    historico = novos[:60]
                    lista_str = ", ".join(f"{v:.2f}x" for v in historico[-30:])
                    msg = f"""*📊 Histórico Aviator PremierBet Atualizado*

[{lista_str}]

**Total:** {len(historico)} rodadas
**Último:** **{historico[-1]:.2f}x**"""
                    enviar_telegram(msg)
                    enviar_print(driver, "📸 Histórico atualizado")

                time.sleep(random.uniform(7, 12))

        except Exception as e:
            erro = traceback.format_exc()
            enviar_telegram(f"🔥 ERRO NO SCRAPER:\n{erro[:800]}")
            time.sleep(8)
        finally:
            try:
                if driver:
                    driver.quit()
            except:
                pass
            enviar_telegram("🔄 Reiniciando scraper em 12s...")
            time.sleep(12)

# ========================= API =========================
@app.route("/api/history")
def get_history():
    return jsonify(historico)

@app.route("/api/last")
def get_last():
    return jsonify(historico[-1] if historico else None)

@app.route("/")
def home():
    return "✅ Scraper Aviator UC v145 rodando firme!"

# ========================= START =========================
if __name__ == "__main__":
    threading.Thread(target=iniciar_scraper, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
