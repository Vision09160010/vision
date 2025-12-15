from loguru import logger

logger.add("logs/myapp.log", format="{time:YYYY-MM-DD at HH:mm:ss} - {level} - {message}", rotation="500MB")

logger.debug("调试信息")
logger.info("正常信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误信息")
logger.level("DEBUG")


try:
    1/0
except Exception as e:
    logger.exception(e)

