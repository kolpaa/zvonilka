import subprocess
import sys
import os
import socket
import webbrowser
import time
import re

def resolve_host():
    """
    Определяем хост для URL без привязки к VPN.
    Приоритет:
      1) Переменные окружения ZVONILKA_HOST / PUBLIC_HOST
      2) Исходящий IP через UDP-сокет (даёт реальный адрес интерфейса)
      3) 'localhost'
    """
    env_host = os.getenv('ZVONILKA_HOST') or os.getenv('PUBLIC_HOST')
    if env_host:
        return env_host.strip()

    # Определяем исходящий IP (без внешних HTTP-запросов)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith(('127.', '169.254.', '0.')):
            return ip
    except Exception:
        pass

    return 'localhost'

def main():
    # Фиксируем рабочую директорию = папка скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Проверяем наличие Python-окружения и зависимостей
    venv_dir = os.path.join(script_dir, '.venv')
    if not os.path.isdir(venv_dir):
        print('Создаём виртуальное окружение...')
        subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
    python_bin = os.path.join(venv_dir, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'python')
    pip_bin = os.path.join(venv_dir, 'Scripts', 'pip.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'pip')
    # Устанавливаем зависимости
    subprocess.check_call([python_bin, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([pip_bin, 'install', '-r', os.path.join(script_dir, 'requirements.txt')])

    # Определяем адрес
    host = resolve_host()
    port = int(os.getenv('ZVONILKA_PORT', '8000'))
    ssl_key = os.path.join(script_dir, 'ssl', 'key.pem')
    ssl_crt = os.path.join(script_dir, 'ssl', 'cert.pem')
    proto = 'https' if (os.path.exists(ssl_key) and os.path.exists(ssl_crt)) or os.getenv('FORCE_HTTPS') == '1' else 'http'
    url = f"{proto}://{host}:{port}/"
    print(f'Открываем браузер: {url}')
    # Открываем браузер чуть позже
    def open_browser():
        time.sleep(2)
        webbrowser.open(url)
    import threading
    if not os.getenv('SKIP_BROWSER'):
        threading.Thread(target=open_browser, daemon=True).start()

    # Запускаем сервер
    env = os.environ.copy()
    env['ZVONILKA_URL'] = url
    subprocess.call([python_bin, os.path.join(script_dir, 'main.py')], env=env)

if __name__ == '__main__':
    main()
