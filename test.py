import logging
import logging.config
#from conn_selenium import conn_link
from conn_selenium import conn_uc, click

logging.config.fileConfig("./log/config/logger.ini", defaults={'filename': './log/mylog.log'},disable_existing_loggers=False)
logger = logging.getLogger(__name__)

url1 =  "https://whoer.net/ru"
url2 = "https://www.cual-es-mi-ip.net/"
url3 = "https://bot.sannysoft.com/"
url_click = "/html/body/h1[2]/a"

driver = conn_uc(headless=False) # Falla el UC con los proxy
#driver.maximize_window()
driver.get(url3)
verifi = click(driver, url_click)
print(verifi)
#driver.save_screenshot( './datadome_undetected_webddriver.png' )

