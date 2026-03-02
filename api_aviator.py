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
    except:
        pass

def clicar_mais_tarde(driver, etapa=""):
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.kumulos-action-button.kumulos-action-button-cancel"))
        )
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
            enviar_telegram("🟢 Iniciando undetected Chrome v145...")

            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36")

            driver = uc.Chrome(version_main=145, options=options)
            wait = WebDriverWait(driver, 60)   # aumentado pra 60s

            # 1. ABRIR PÁGINA
            driver.get(URL)
            enviar_telegram("🌐 Página aberta!")
            time.sleep(20)                     # +5s extras
            enviar_print(driver, "📸 1. Página carregada")

            # 2. MAIS TARDE INICIAL
            clicar_mais_tarde(driver, "(início)")
            time.sleep(10)                     # espera extra após clique
            enviar_print(driver, "📸 2. Após Mais Tarde inicial")

            # ==================== REMOVER OVERLAY ====================
            try:
                mask = driver.find_element(By.CSS_SELECTOR, "div.kumulos-background-mask")
                driver.execute_script("arguments[0].style.display = 'none';", mask)
                enviar_telegram("✅ Overlay removido")
                enviar_print(driver, "📸 Overlay removido")
            except:
                pass

            # ==================== LOGIN (AGORA SUPER ROBUSTO) ====================
            enviar_telegram("🔑 Tentando login...")
            enviar_print(driver, "📸 3. Antes de procurar campos de login")

            login_ok = False
            try:
                # Campo telefone
                login_input = WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.NAME, "login"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_input)
                time.sleep(2)
                login_input.click()
                login_input.send_keys(Keys.CONTROL + "a")
                login_input.send_keys(Keys.BACKSPACE)
                for char in LOGIN:
                    login_input.send_keys(char)
                    time.sleep(0.08)
                enviar_print(driver, "📸 4. Número preenchido")

                # Campo senha
                pwd = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pwd)
                time.sleep(2)
                pwd.click()
                pwd.send_keys(Keys.CONTROL + "a")
                pwd.send_keys(Keys.BACKSPACE)
                for char in PASSWORD:
                    pwd.send_keys(char)
                    time.sleep(0.08)
                enviar_print(driver, "📸 5. Senha preenchida")

                # Botão
                btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.form-button.form-button--primary"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(2)
                try:
                    btn.click()
                except:
                    driver.execute_script("arguments[0].click();", btn)

                enviar_telegram("✅ Botão Login clicado!")
                enviar_print(driver, "📸 6. Botão Login clicado")
                login_ok = True
                time.sleep(25)

            except Exception as e:
                enviar_telegram(f"⚠️ Login não apareceu ou erro: {type(e).__name__}")
                enviar_print(driver, "📸 ERRO no login - pulando para iframe")
                time.sleep(15)

            # 7. MAIS TARDE APÓS LOGIN (mesmo se login falhou)
            clicar_mais_tarde(driver, "(após login)")

            # ==================== IFRAME ====================
            iframe_ok = False
            try:
                iframe = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.casino-game-launch-iframe__frame"))
                )
                driver.switch_to.frame(iframe)
                enviar_telegram("✅ Entrou no iframe específico")
                enviar_print(driver, "📸 7. Entrou no iframe")
                iframe_ok = True
            except:
                enviar_telegram("⚠️ Iframe principal falhou → tentando fallback")
                enviar_print(driver, "📸 Tentando fallback iframe")
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    driver.switch_to.frame(iframes[-1])
                    enviar_telegram("✅ Entrou no iframe (fallback)")
                    enviar_print(driver, "📸 7. Entrou no iframe (fallback)")
                    iframe_ok = True

            # ==================== LOOP HISTÓRICO ====================
            while True:
                clicar_mais_tarde(driver, "(loop)")

                if not iframe_ok:
                    iframe = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.casino-game-launch-iframe__frame"))
                    )
                    driver.switch_to.frame(iframe)
                    iframe_ok = True

                items_wrapper = WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div._itemsWrapper_7l84e_35"))
                )

                buttons = items_wrapper.find_elements(
                    By.CSS_SELECTOR, "button._container_12jzl_1 span._container_1p5jb_1"
                )

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
                    msg = f"""*📊 Histórico Aviator PremierBet Atualizado*

[{lista_str}]

**Total:** {len(historico)} rodadas
**Último:** **{historico[-1]:.2f}x**"""
                    enviar_telegram(msg)
                    enviar_print(driver, "📸 8. Histórico atualizado")

                time.sleep(random.uniform(7, 12))

        except Exception as e:
            erro = traceback.format_exc()
            enviar_telegram(f"🔥 ERRO CRÍTICO:\n{erro[:700]}")
            if driver:
                enviar_print(driver, "📸 ERRO CRÍTICO")
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
    return "✅ Scraper Aviator v145 - Login reforçado!"

# ========================= START =========================
if __name__ == "__main__":
    threading.Thread(target=iniciar_scraper, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
