# Zvonilka - Простые видеозвонки

Легкое веб‑приложение для видеозвонков на WebRTC с бэкендом на FastAPI и статичной HTML‑страницей.

## 🚀 Возможности

- 📱 Видеозвонки через браузер (двое участников)
- 🔗 Создание и присоединение к комнатам
- 🎥 Видео и аудио P2P (WebRTC)
- 🌐 Красочный Y2K интерфейс

## 📦 Технологии

- Python 3.9+
- FastAPI + Uvicorn
- WebRTC (в браузере)
- Чистый HTML/CSS/JS

## 🛠️ Установка и запуск

### Быстрый запуск

```bash
chmod +x start.sh
./start.sh
```

По умолчанию сервер запустится на http://localhost:8000

Для работы камеры вне localhost требуется HTTPS (см. ниже).

### Режим разработки (autoreload)

```bash
chmod +x dev.sh
./dev.sh
```

- Dev HTTP: http://localhost:8000
- Если в папке ssl/ есть key.pem и cert.pem — Dev HTTPS: https://localhost:8000

## 🔐 HTTPS

Для доступа к камере/микрофону в браузере за пределами localhost нужен HTTPS.

Сгенерировать самоподписанный сертификат:

```bash
chmod +x generate_ssl.sh
./generate_ssl.sh            # CN=localhost, SAN включает 127.0.0.1 и пример IP 10.8.1.13
# или укажите CN и SAN явно:
./generate_ssl.sh my-vpn.example.com "DNS:my-vpn.example.com,IP:10.8.1.13,IP:127.0.0.1"
```

После этого запустите сервер как обычно. Если файлы ssl/key.pem и ssl/cert.pem найдены — сервер поднимется по HTTPS.

## 🎯 Как пользоваться

1. Откройте http(s)://<IP_ИЛИ_DNS>:<PORT>
2. Если вы находитесь в Amnezia VPN — укажите IP сервера VPN и порт (по умолчанию 8000) и подключитесь.
3. Создайте комнату или введите существующий ID.
4. Когда оба участника в комнате — нажмите «Начать звонок».

Страница для проверки подключения: http(s)://<IP_ИЛИ_DNS>:<PORT>/test

## 🔧 API

- WebSocket: ws(s)://<HOST>:<PORT>/ws/{user_id}
- GET /api/generate-room — создает новый room_id

Сообщения WebSocket:
- join_room, leave_room, offer, answer, ice_candidate, hangup

## 📱 Совместимость

- Chrome, Firefox, Edge, Safari (современные версии)

## 🐛 Известные моменты

- Для видеозвонка вне localhost обязателен HTTPS
- Поддерживаются звонки 1:1 (двое участников)

## 📄 Лицензия

MIT
