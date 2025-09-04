import subprocess
import sys
import os
import socket
import webbrowser
import time
import re

def find_vpn_ip():
    # Ищем первый IP вида 10.8.x.x среди всех интерфейсов
    import psutil
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and re.match(r"^10\.8\.\d+\.\d+$", addr.address):
                return addr.address
    return 'localhost'

def main():
    # Проверяем наличие Python-окружения и зависимостей
    venv_dir = os.path.join(os.path.dirname(__file__), '.venv')
    if not os.path.isdir(venv_dir):
        print('Создаём виртуальное окружение...')
        subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
    python_bin = os.path.join(venv_dir, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'python')
    pip_bin = os.path.join(venv_dir, 'Scripts', 'pip.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'pip')
    # Устанавливаем зависимости
    subprocess.check_call([python_bin, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([pip_bin, 'install', '-r', 'requirements.txt'])

    # Определяем адрес
    host = find_vpn_ip()
    port = 8000
    proto = 'http'
    if os.path.exists('ssl/key.pem') and os.path.exists('ssl/cert.pem'):
        proto = 'https'
    url = f"{proto}://{host}:{port}/"
    print(f'Открываем браузер: {url}')
    # Открываем браузер чуть позже
    def open_browser():
        time.sleep(2)
        webbrowser.open(url)
    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Запускаем сервер
    env = os.environ.copy()
    env['ZVONILKA_URL'] = url
    subprocess.call([python_bin, 'main.py'], env=env)

if __name__ == '__main__':
    try:
        import psutil
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
    main()
