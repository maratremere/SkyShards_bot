import logging

logger = logging.getLogger("tg_bot")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("core/bot.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#logger.basicConfig(
#    filename='bot.log',            # файл, куда пишем логи
#    level=logging.INFO,            # минимальный уровень сообщений
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#)