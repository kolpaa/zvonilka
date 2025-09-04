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

echo "✅ Запускаем сервер..."
python3 main.py
