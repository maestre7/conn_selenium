from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

""" from pathlib import Path
print(Path('./webdriver/chromedriver.exe')) """
#driver = webdriver.Chrome(executable_path=Path('./webdriver/chromedriver.exe'))
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("http://selenium.dev")