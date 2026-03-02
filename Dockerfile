FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    libnss3 libgconf-2-4 libxi6 libxcomposite1 libxcursor1 \
    libxdamage1 libxrandr2 libasound2 libpangocairo-1.0-0 \
    libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libdrm2 libxkbcommon0 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Instala Google Chrome oficial (melhor compatibilidade com undetected)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir flask selenium requests undetected-chromedriver

ENV PYTHONUNBUFFERED=1

CMD ["python", "api_aviator.py"]
