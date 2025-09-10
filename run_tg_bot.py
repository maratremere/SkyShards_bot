from watchgod import run_process
import subprocess
import logging
import time

from core.logger import logger

def run_bot():
    logger.info("Restart bot...")
    #Запуск main.py через subprocess, вывод сразу в stdout
    subprocess.run(['python', '-u', 'main.py'])

if __name__ == "__main__":
    logger.info("watchgod launched, monitoring changes...")
    #Слежение за текущей папкой
    run_process('.', run_bot)
