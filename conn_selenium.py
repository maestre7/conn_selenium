
import os
import logging
from time import sleep
from shutil import copyfile
from pathlib import Path
from random import choice

import undetected_chromedriver.v2 as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException
from webdrivermanager import ChromeDriverManager  #Actualiza los webdriver del selenium
from fake_useragent import UserAgent, FakeUserAgentError
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy


logger = logging.getLogger(__name__)


def conexion(chromedriver = 'sele/webdriver/chromedriver.exe', headless = True, proxy = False):
    '''Establecemos conexion con selenium, usando los webdriver indicados.
        chromedriver = drivers usados por el selenium ej:'./chromedriver.exe'
        headless = ejecutar en primer plano(False) o segundo plano(True).
        proxy = True/False o una ip:port
    '''

    driver = None

    try:
        options = Options()
        options.add_argument('--ignore-certificate-errors') # Desabilitamos para que no de error en headless
        options.add_argument('--ignore-ssl-errors') # Desabilitamos para que no de error en headless
        options.add_argument('--disable-notifications') # Desabilitamos para evitar las ventanas de notifications
        options.add_argument('--no-sandbox') # Desabilitamos la Privacy Sandbox para no dar problemas la automation
        options.add_argument('--verbose') # Desabilitamos registro detallado para no llenar la consola
        options.add_argument('--disable-gpu') # Desabilitamos la mejora de renderizado no la necesitamos en headless
        options.add_argument('--disable-extensions') # Desabilitamos la extensions para no dar pistas sobre la automation
        options.add_argument('--disable-software-rasterizer') # software de rastreo???
        options.add_argument('--start-maximized') # Maximizamos pantalla para no dar pistas sobre la automation
        options.add_argument('--disable-dev-shm-usage') # Desabilitamos modo desarrollador no lo necesitamos en headless
        options.add_argument('--disable-infobars') # Desabilitamos la barra de que informa sobre la automation

        try:
            ua = UserAgent()
        except FakeUserAgentError:
            logger.exception("FakeUserAgentError")
            userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        else:
            userAgent = ua.random
        finally:
            options.add_argument(f'user-agent={userAgent}')
      
        if proxy != False: #str(ip:port)
            if proxy == True:
                req_proxy = RequestProxy() #you may get different number of proxy when  you run this at each time
                proxies = req_proxy.get_proxy_list() #this will create proxy list
                PROXY = proxies[choice(range(len(proxies)))].get_address()
            else:
                PROXY = proxy

            capabilities = dict(DesiredCapabilities.CHROME)
            capabilities['proxy'] = {'proxyType': 'MANUAL',
                                    'httpProxy': PROXY,
                                    'ftpProxy': PROXY,
                                    'sslProxy': PROXY,
                                    'noProxy': '',
                                    'class': "org.openqa.selenium.Proxy",
                                    'autodetect': False}

        if headless:
            options.headless = True # Modo sin ventanas (segundo plano)
   
        driver = webdriver.Chrome(executable_path = Path(chromedriver), options = options) 
        
    except (SessionNotCreatedException, OSError):
        ok = actualiza_webdriver(chromedriver)

        if ok:
            driver = conexion(chromedriver, headless)
        else:
            logger.exception('Conn_selenium')
        
    except WebDriverException:
        logger.exception('Conn_selenium')
        driver = False
    finally:
        return driver
        
        
def actualiza_webdriver(chromedriver):
    '''Descarga los webdriver actualizados y los copia a la ubicacion especificada
    
    chromedriver: Path de los webdriver o posicion donde los deseamos alojar. STR o PATH
    '''
    
    salida = None
    
    try:
        CDM = ChromeDriverManager()
        url_filename = CDM.download_and_install()
        
        c = Path(chromedriver)
        
        if os.path.exists(c):
            os.remove(c)
            
        copyfile(Path(url_filename[1]), c)
        
    except OSError:
        logger.exception('actualiza_webdriver')
        salida = False
    else:
        logger.info(f'actualiza_webdriver: OK, {url_filename}')
        salida = True
    finally:
        return salida
        
        
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
    finally:
        return salida
        
    
def click(driver, xpath, wait_time = 30, control = False, log = True):
    '''Click en un xpath de selenium '''
    
    salida = None

    try:
        """ if type(wait_time) is int: """
        if isinstance(wait_time, int):
            wait = WebDriverWait(driver, wait_time)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

        if control is False:
            driver.find_element_by_xpath(xpath).click()
        else:
            driver.find_elements_by_xpath(xpath)[control].click()
               
    except (TimeoutException, ElementClickInterceptedException, AttributeError):
        if log:
            logger.exception(f'click False: {xpath}')
        else:
            logger.info(f'click False: {xpath}')
        salida = False
    else:
        logger.info(f'click True: {xpath}')
        salida = True
    finally:
        return salida
        
        
def submit(driver, xpath, wait_time = 30):
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
    finally:
        return salida
        
        
def keys(driver, xpath, keys, enter = False, wait_time = 30):
    '''Keys en un xpath de selenium '''
    
    salida = None
    
    try:
        if type(wait_time) is int:
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
    finally:
        return salida
        
        
def recoger_elementos(driver, xpath, wait_time = 30, control = 'all', log = True):
    '''Recogemos los elementos asociados al Xpath '''
    
    salida = None
    
    try:
        if type(wait_time) is int:
            wait = WebDriverWait(driver, wait_time)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

        if control == 'all': #Diferenciamos de todas las coincidencias o una en concreto
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
    finally:
        return salida 
       
        
def recoger_elemento(driver, xpath, wait_time = 30):
    '''Recogemos el elemento asociados al Xpath '''
    
    salida = None
    
    try:
        """ if type(wait_time) is int: """ 
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
    finally:
        return salida 
        
        
def forzar_carga(driver, wait_time = 0.1):
    '''Bajamos y subimos para obligar a la carga de todas los elementos '''   
    
    salida = None
    scheight = 0.1
    
    try:
        while scheight < 9.9:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
            scheight += .1
            sleep(wait_time)
            
        salida = True
            
    except (WebDriverException, ElementClickInterceptedException):
        logger.exception('forzar_carga')
        salida = False
    else:
        logger.info('forzar_carga: OK')
    finally:
        return salida 
        
        
def centrar_scroll(wde, wait_time = 0.5):
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
    finally:
        return salida 
        
        
def headers(driver):
    '''Recuperamos las cabeceras de la web'''
    salida = None

    try:
        headers = driver.execute_script("var req = new XMLHttpRequest();req.open('GET', document.location, false);req.send(null);return req.getAllResponseHeaders()")
        salida = headers #.splitlines()

    except WebDriverException:
        logger.exception('headers')
        salida = False
    else:
        logger.info('headers OK')
    finally:
        return salida
        

def conexion_uc(folder = False, headless = True, proxy = False):
    '''conexion con selenium ataves del modulo undetected_chromedriver'''

    try:
        # uc.ChromeOptions() no funciona con los proxy
        # webdriver.ChromeOptions() no parece funcionar el proxy???, ni funciona headless
        options = webdriver.ChromeOptions() # comprobar si funciona los proxies

        t_folder = os.path.abspath('./sele/uc') if folder is False else folder

        p_folder = Path(t_folder)
        if not p_folder.exists():
            p_folder.mkdir()

        options.user_data_dir = str(t_folder)
        
        try:
            ua = UserAgent()
        except FakeUserAgentError:
            logger.exception("FakeUserAgentError")
            userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        else:
            userAgent = ua.random
        finally:
            options.add_argument(f'user-agent={userAgent}')
    
        if proxy != False: #str(ip:port)
            if proxy == True:
                req_proxy = RequestProxy() #you may get different number of proxy when  you run this at each time
                proxies = req_proxy.get_proxy_list() #this will create proxy list
                PROXY = proxies[choice(range(len(proxies)))].get_address()
            else:
                PROXY = proxy

            capabilities = dict(DesiredCapabilities.CHROME)
            capabilities['proxy'] = {'proxyType': 'MANUAL',
                                    'httpProxy': PROXY,
                                    'ftpProxy': PROXY,
                                    'sslProxy': PROXY,
                                    'noProxy': '',
                                    'class': "org.openqa.selenium.Proxy",
                                    'autodetect': False}

        #options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        # Desabilitamos para evitar las pantallas gris
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions') # Desabilitamos la extensions para no dar pistas sobre la automation
        options.add_argument('--disable-dev-shm-usage') # Desabilitamos modo desarrollador no lo necesitamos en headless
        #--------
        #options.add_argument("--no-sandbox")
        #options.add_argument('--disable-notifications') # Desabilitamos para evitar las ventanas de notifications
            
        if headless:
            options.headless = True # Modo sin ventanas (segundo plano)
   
        driver = uc.Chrome(options = options)
        
    except (SessionNotCreatedException, OSError, WebDriverException):
        logger.exception('Conexion_uc')
        driver = False
    finally:
        return driver