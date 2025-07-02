import asyncio
import subprocess

from aiorun import run
from watchfiles import arun_process

def start_bot():
    # Запуск основного скрипта, как ты его обычно запускаешь
    # python -m main
    subprocess.run(['python', '-m', 'main'])

async def main():
    print("👀 Старт arun_process")
    await arun_process(
        'app',
        'config',
        'dev_runner.py',
        'main.py',
        target=start_bot, # 'dev_runner:main'
        watch_filter=lambda change, path: not path.endswith(('.db', '.db-wal', '.db-shm', '.db-journal')),
        debounce=1000,
    )

if __name__ == '__main__':
    # asyncio.run(main())
    run(main())
