
import os
import logging
from time import sleep
from shutil import copyfile
from pathlib import Path
from random import choice

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException
# Actualiza los webdriver del selenium
#from webdrivermanager import ChromeDriverManager
from webdriver_manager.chrome import ChromeDriverManager
#from fake_useragent import UserAgent, FakeUserAgentError
# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy


logger = logging.getLogger(__name__)

def conn_uc(headless: bool=True, folder: bool = False) -> webdriver.Chrome:
    '''Selenium connection through undetected_chromedriver module'''

    driver = False

    try:
        # uc.ChromeOptions() no funciona con los proxy
        # webdriver.ChromeOptions() no parece funcionar el proxy???, ni funciona headless
        #options = webdriver.ChromeOptions()  # comprobar si funciona los proxies
        options = uc.ChromeOptions()

        # Folder install UC
        temp_folder = os.path.abspath('./uc') if folder is False else folder
        path_folder = Path(temp_folder)
        if not path_folder.exists():
            path_folder.mkdir()

        options.user_data_dir = str(temp_folder) # setting profile

        if headless:
            options.headless = True  # Windowless mode (second plane)

        driver = uc.Chrome(options=options)

        driver.maximize_window() # Maximize screen

    except (SessionNotCreatedException, OSError, WebDriverException):
        logger.exception('Conn_uc')
        driver = False

    return driver


def conn_link(headless: bool = True) -> webdriver.Chrome:
    '''We establish connection with selenium, using the indicated webdriver.'''

    driver = False

    try:
        options = Options()
        
        if headless:
            options.headless = True  # Windowless mode (second plane)

        # Actualiza los webdrivers automaticamente
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        driver.maximize_window() # Maximize screen

    except (SessionNotCreatedException, OSError, WebDriverException):
        logger.exception('Conn_selenium - conn_link')
        driver = False

    return driver


def click(driver: webdriver.Chrome, 
          xpath: str, 
          wait_time: float = 30, 
          control: int|bool = False, 
          log: bool = True) -> bool:
    '''Click on a selenium xpath,
    driver: drivers to run selenium
    xpath: node element position in xpath format
    wait_time: waiting time before giving error
    control: position it occupies in a list of being in a
    log: report as exception or information only
    return: si pudo o no hacer clic en el elemento
    '''

    salida = False

    try:
        # if type(wait_time) is int:
        #if isinstance(wait_time, float, int):
        wait = WebDriverWait(driver, wait_time)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

        if control is False: # if it occupies a position in a list or not
            driver.find_element(By.XPATH, xpath).click() #find_element_by_xpath(xpath).click()
        else:
            driver.find_elements(By.XPATH, xpath)[control].click()

    except (TimeoutException, ElementClickInterceptedException, AttributeError):
        if log: # report as exception or information only
            logger.exception(f'click False: {xpath}')
        else:
            logger.info(f'click False: {xpath}')

        salida = False

    else:
        logger.info(f'click True: {xpath}')
        salida = True

    return salida


def submit(driver, xpath, wait_time=30):
    '''Submit en un xpath de selenium '''

    salida = None

    try:
        wait = WebDriverWait(driver, wait_time)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.find_element_by_xpath(xpath).submit()
        salida = True

    except (TimeoutException, ElementClickInterceptedException, AttributeError):
        logger.exception(f'submit False: {xpath}')
        salida = False
    else:
        logger.info(f'submit True: {xpath}')

    return salida


def keys(driver, xpath, keys, enter=False, wait_time=30):
    '''Keys en un xpath de selenium '''

    salida = None

    try:
        # if type(wait_time) is int:
        if isinstance(wait_time, int):
            wait = WebDriverWait(driver, wait_time)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

        if enter:
            driver.find_element_by_xpath(xpath).send_keys(keys + Keys.ENTER)
        else:
            driver.find_element_by_xpath(xpath).send_keys(keys)

        salida = True

    except (TimeoutException, ElementClickInterceptedException, AttributeError):
        logger.exception(f'keys: {xpath}, {keys}, {enter}')
        salida = False
    else:
        logger.info(f'keys OK: {xpath}, {keys}, {enter}')

    return salida


def recoger_elementos(driver, xpath, wait_time=30, control='all', log=True):
    '''Recogemos los elementos asociados al Xpath '''

    salida = None

    try:
        # if type(wait_time) is int:
        if isinstance(wait_time, int):
            wait = WebDriverWait(driver, wait_time)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

        if control == 'all':  # Diferenciamos de todas las coincidencias o una en concreto
            elementos = driver.find_elements_by_xpath(xpath)
        else:
            elementos = driver.find_elements_by_xpath(xpath)[control]

        salida = elementos

    except (TimeoutException, ElementClickInterceptedException, AttributeError):
        if log:
            logger.exception(f'recoger_elementos False: {xpath}')
        else:
            logger.info(f'recoger_elementos False: {xpath}')
        salida = False
    else:
        logger.info(f'recoger_elementos True: {xpath}')
    
    return salida


def recoger_elemento(driver, xpath, wait_time=30):
    '''Recogemos el elemento asociados al Xpath '''

    salida = None

    try:
        # if type(wait_time) is int:
        if isinstance(wait_time, int):
            wait = WebDriverWait(driver, wait_time)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

        elemento = driver.find_element_by_xpath(xpath)
        salida = elemento

    except (TimeoutException, ElementClickInterceptedException, AttributeError):
        logger.exception(f'recoger_elemento False: {xpath}')
        salida = False
    else:
        logger.info(f'recoger_elemento True: {xpath}')
    
    return salida


def forzar_carga(driver, wait_time=0.1):
    '''Bajamos y subimos para obligar a la carga de todas los elementos '''

    salida = None
    scheight = 0.1

    try:
        while scheight < 9.9:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
            scheight += .1
            sleep(wait_time)

        salida = True

    except (WebDriverException, ElementClickInterceptedException):
        logger.exception('forzar_carga')
        salida = False
    else:
        logger.info('forzar_carga: OK')
    
    return salida


def centrar_scroll(wde: webdriver, wait_time: float=0.5):
    '''Centramos el scroll en el webdriver_element '''

    salida = None

    try:
        wde.location_once_scrolled_into_view

        if wait_time != None:
            sleep(wait_time)

        salida = True

    except (WebDriverException, ElementClickInterceptedException):
        logger.exception('centrar_scroll')
        salida = False
    else:
        logger.info('centrar_scroll: OK')
    
    return salida


def headers(driver):
    '''Recuperamos las cabeceras de la web'''
    salida = None

    try:
        headers = driver.execute_script(
            "var req = new XMLHttpRequest();req.open('GET', document.location, false);req.send(null);return req.getAllResponseHeaders()")
        salida = headers  # .splitlines()

    except WebDriverException:
        logger.exception('headers')
        salida = False
    else:
        logger.info('headers OK')
    
    return salida


    
    


def random_user_agent(options):
    """"we add a random user agent, if we give an error we add 
    a fixed one different from the default of the original browser. 
    """

    try:
        ua = UserAgent()
    except FakeUserAgentError:
        logger.exception("FakeUserAgentError")
        userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    else:
        userAgent = ua.random
    finally:
        options.add_argument(f'user-agent={userAgent}')

    return options


def random_proxy(proxy):
    PROXY = None

    try:
        if proxy == True:
            # you may get different number of proxy when  you run this at each time
            req_proxy = RequestProxy()
            proxies = req_proxy.get_proxy_list()  # this will create proxy list
            PROXY = proxies[choice(range(len(proxies)))].get_address()
        else:
            PROXY = proxy

    except (SessionNotCreatedException, OSError, WebDriverException):
        logger.exception('random_proxy')
    
    return PROXY

def xpath_posicional(xpath, control):
    '''Ajustamos un xpath que necesita una posicion de control '''

    salida = None

    try:
        eslabon = xpath.split(sep='[]')
        salida = f'{eslabon[0]}[{control}]{eslabon[1]}'

    except (ValueError, AttributeError, TypeError):
        logger.exception(f'xpath_posicional: {xpath}, {control}')
        salida = False
    else:
        logger.info(f'xpath_posicional: OK, {xpath}, {control}')

    return salida
