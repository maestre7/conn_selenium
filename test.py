import logging
import logging.config
from conn_selenium import conn_link

logging.config.fileConfig("./log/config/logger.ini", defaults={'filename': './log/mylog.log'},disable_existing_loggers=False)
logger = logging.getLogger(__name__)

url1 =  "https://whoer.net/ru"
url2 = "https://www.cual-es-mi-ip.net/"
url3 = "https://bot.sannysoft.com/"

driver = conn_link(headless = False, proxy = True) # Falla el UC con los proxy

driver.get(url2)
