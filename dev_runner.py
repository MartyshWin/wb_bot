import asyncio
import subprocess

from watchfiles import arun_process

def start_bot():
    # Запуск основного скрипта, как ты его обычно запускаешь
    # python -m main
    subprocess.run(['python', '-m', 'main'])

async def main():
    await arun_process('.', target=start_bot)

if __name__ == '__main__':
    asyncio.run(main())