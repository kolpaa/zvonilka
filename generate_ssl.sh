#!/bin/bash

set -e

echo "🔐 Генерация SSL сертификата для HTTPS..."

# Использование: ./generate_ssl.sh [CN] [SANs через запятую]
# Пример: ./generate_ssl.sh my-vpn.example.com "DNS:my-vpn.example.com,IP:10.8.1.13,IP:127.0.0.1"

CN=${1:-localhost}
SAN_INPUT=${2:-"DNS:localhost,DNS:*.local,IP:127.0.0.1,IP:10.8.1.13"}

# Создаем директорию для сертификатов
mkdir -p ssl

# Генерируем самоподписанный сертификат
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
  -subj "/C=RU/ST=State/L=City/O=Zvonilka/OU=IT/CN=${CN}" \
  -addext "subjectAltName=${SAN_INPUT}"

chmod 600 ssl/key.pem

echo "✅ SSL сертификат создан в папке ssl/"
printf "📄 CN: %s\n🔖 SAN: %s\n" "$CN" "$SAN_INPUT"
echo "🌐 Теперь сервер может работать по HTTPS"
