import os
import time
import traceback
import threading
import re
import requests
from flask import Flask, jsonify

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

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

def enviar_print(driver, legenda="📸 Screenshot"):
    try:
        path = "/tmp/print.png"
        driver.save_screenshot(path)
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                      files={"photo": open(path, "rb")},
                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": legenda})
    except:
        pass

def clicar_mais_tarde(driver, etapa=""):
    try:
        btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.kumulos-action-button.kumulos-action-button-cancel")))
        btn.click()
        enviar_telegram(f"✅ Mais Tarde clicado {etapa}")
        enviar_print(driver, f"📸 Mais Tarde clicado {etapa}")
        time.sleep(2)
        return True
    except:
        return False

# ========================= SCRAPER =========================
def iniciar_scraper():
    global historico
    while True:
        driver = None
        try:
            enviar_telegram("🟢 Iniciando undetected Chrome v145 (TURBO + ANTI-RESTART)...")

            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36")

            driver = uc.Chrome(version_main=145, options=options)
            wait = WebDriverWait(driver, 45)

            driver.get(URL)
            enviar_telegram("🌐 Página aberta!")
            time.sleep(8)
            enviar_print(driver, "📸 1. Página carregada")

            clicar_mais_tarde(driver, "(início)")
            time.sleep(5)
            enviar_print(driver, "📸 2. Após Mais Tarde inicial")

            # REMOVER OVERLAY
            try:
                mask = driver.find_element(By.CSS_SELECTOR, "div.kumulos-background-mask")
                driver.execute_script("arguments[0].style.display = 'none';", mask)
            except:
                pass
            time.sleep(2)

            # ==================== LOGIN TURBO (INSTANTÂNEO) ====================
            enviar_telegram("🔑 Tentando login...")
            enviar_print(driver, "📸 3. Antes do login")

            try:
                # Login rápido com JS + send_keys direto
                login_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))
                driver.execute_script("arguments[0].value = '';", login_input)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_input)
                login_input.send_keys(LOGIN)
                enviar_print(driver, "📸 4. Número preenchido (rápido)")

                pwd = wait.until(EC.presence_of_element_located((By.NAME, "password")))
                driver.execute_script("arguments[0].value = '';", pwd)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pwd)
                pwd.send_keys(PASSWORD)
                enviar_print(driver, "📸 5. Senha preenchida (rápido)")

                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.form-button.form-button--primary")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                try:
                    btn.click()
                except:
                    driver.execute_script("arguments[0].click();", btn)

                enviar_telegram("✅ 6. Login enviado!")
                enviar_print(driver, "📸 6. Login enviado")
                time.sleep(20)   # tempo necessário pro jogo carregar

            except:
                enviar_telegram("⚠️ Login pulado")
                enviar_print(driver, "📸 Login pulado")
                time.sleep(12)

            clicar_mais_tarde(driver, "(após login)")

            # ==================== IFRAME COM RETRY FORTE (NÃO REINICIA MAIS) ====================
            enviar_telegram("🎯 Aguardando iframe...")
            iframe_ok = False
            for tentativa in range(6):  # 6 tentativas
                try:
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.casino-game-launch-iframe__frame"))
                    )
                    driver.switch_to.frame(iframe)
                    enviar_telegram("✅ 7. Entrou no iframe!")
                    enviar_print(driver, "📸 7. Entrou no iframe")
                    iframe_ok = True
                    break
                except:
                    enviar_telegram(f"⚠️ Tentativa {tentativa+1}/6 - iframe ainda não apareceu")
                    if tentativa < 4:
                        driver.refresh()
                        time.sleep(8)
                    else:
                        # fallback
                        iframes = driver.find_elements(By.TAG_NAME, "iframe")
                        if iframes:
                            driver.switch_to.frame(iframes[-1])
                            enviar_telegram("✅ 7. Iframe fallback OK")
                            enviar_print(driver, "📸 7. Iframe fallback")
                            iframe_ok = True
                            break
                    time.sleep(6)

            if not iframe_ok:
                raise Exception("Iframe falhou após 6 tentativas")

            enviar_telegram("🚀 Iniciando captura do histórico (a cada 5s)!")
            enviar_print(driver, "📸 8. Monitoramento iniciado")

            # ==================== LOOP HISTÓRICO (5 SEGUNDOS) ====================
            while True:
                clicar_mais_tarde(driver, "(loop)")
                time.sleep(1)

                items_wrapper = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div._itemsWrapper_7l84e_35"))
                )
                buttons = items_wrapper.find_elements(By.CSS_SELECTOR, "button._container_12jzl_1 span._container_1p5jb_1")

                novos = []
                for span in buttons:
                    txt = span.text.strip()
                    if txt:
                        match = re.search(r'(\d+\.?\d*)', txt)
                        if match:
                            novos.append(float(match.group(1)))

                if novos and (not historico or novos != historico):
                    historico = novos
                    lista_str = ", ".join(f"{v:.2f}x" for v in historico[-30:])
                    msg = f"""*📊 Histórico Aviator Atualizado*

[{lista_str}]

Total: **{len(historico)}** | Último: **{historico[-1]:.2f}x**"""
                    enviar_telegram(msg)
                    enviar_print(driver, "📸 Histórico atualizado")

                time.sleep(5)

        except Exception as e:
            enviar_telegram(f"🔥 ERRO: {type(e).__name__} → reiniciando")
            if driver:
                try:
                    enviar_print(driver, "📸 ERRO")
                except:
                    pass
        finally:
            try:
                if driver:
                    driver.quit()
            except:
                pass
            enviar_telegram("🔄 Reiniciando scraper em 8s...")
            time.sleep(8)

# ========================= API =========================
@app.route("/api/history")
def get_history():
    return jsonify(historico)

@app.route("/api/last")
def get_last():
    return jsonify(historico[-1] if historico else None)

@app.route("/")
def home():
    return "✅ Scraper Aviator TURBO + ANTI-RESTART rodando!"

# ========================= START =========================
if __name__ == "__main__":
    threading.Thread(target=iniciar_scraper, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
