#!/bin/bash

set -e

echo "🔧 Запуск в режиме разработки..."

# Создать и активировать окружение
if [ ! -d ".venv" ]; then
    echo "📦 Создаем виртуальное окружение Python (.venv)..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Подсказка по HTTPS
if [ ! -f "ssl/key.pem" ] || [ ! -f "ssl/cert.pem" ]; then
    echo "⚠️  SSL сертификаты не найдены. В dev можно работать на http://localhost:8000"
fi

# Запуск с авто-перезапуском
export PYTHONUNBUFFERED=1
python - <<'PY'
import os
import uvicorn

ssl_keyfile = "ssl/key.pem"
ssl_certfile = "ssl/cert.pem"

if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
    print("🔐 Dev HTTPS на https://localhost:8000 (autoreload)")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True,
                ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
else:
    print("▶️  Dev HTTP на http://localhost:8000 (autoreload)")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
PY
