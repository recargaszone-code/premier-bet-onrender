FROM python:3.11-bullseye

# Instalar Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    libgtk-3-0 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgbm1 \
    libxkbcommon0 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome estável (funciona melhor que chromium)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install flask selenium undetected-chromedriver requests gunicorn

ENV PORT=5000
ENV CHROME_BIN=/usr/bin/google-chrome

CMD ["python", "api_aviator.py"]
