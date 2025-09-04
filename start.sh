#!/bin/bash

set -e

echo "🚀 Запуск сервера Zvonilka..."

# Проверяем, установлены ли зависимости Python
if [ ! -d ".venv" ]; then
    echo "📦 Создаем виртуальное окружение Python (.venv)..."
    python3 -m venv .venv
fi

echo "🔧 Активируем виртуальное окружение..."
source .venv/bin/activate

echo "📋 Устанавливаем зависимости Python..."
pip install -r requirements.txt

# Подсказка по HTTPS
if [ ! -f "ssl/key.pem" ] || [ ! -f "ssl/cert.pem" ]; then
    echo "⚠️  SSL сертификаты не найдены. Для работы камеры в браузере вне localhost нужен HTTPS."
    echo "👉 Сгенерируйте сертификаты: ./generate_ssl.sh [IP_ИЛИ_DNS]"
fi

# Формируем URL для открытия в браузе
PORT="8000"
PROTO="http"
# Автоматически ищем VPN-IP (например, 10.8.*.*)
VPN_IP=$(hostname -I | tr ' ' '\n' | grep -m1 -E '^10\.8\.[0-9]+\.[0-9]+$')
if [ -n "$VPN_IP" ]; then
    HOST="$VPN_IP"
else
    HOST="localhost"
fi
if [ -f "ssl/key.pem" ] && [ -f "ssl/cert.pem" ]; then
    PROTO="https"
    # Можно оставить тот же HOST (VPN-IP или localhost)
fi

if [ -n "$ZVONILKA_URL" ]; then
    URL="$ZVONILKA_URL"
else
    URL="${PROTO}://${HOST}:${PORT}/"
fi

# Пытаемся автоматически открыть браузер (Linux)
if command -v xdg-open >/dev/null 2>&1; then
    ( sleep 2; xdg-open "$URL" >/dev/null 2>&1 || true ) &
    echo "🌐 Открываем браузер: $URL"
else
    echo "ℹ️ Откройте в браузере: $URL"
fi

echo "✅ Запускаем сервер..."
python3 main.py
