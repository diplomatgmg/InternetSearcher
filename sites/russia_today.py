import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()

driver.get("https://russian.rt.com/news")

advertising_banner = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[1]/img")))

advertising_banner.click()


advertising_banner = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[5]/div/a")))

advertising_banner.click()

while True:
    try:
        button = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/div[2]/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/a")))

        button.click()
        time.sleep(0.1)
    except:
        pass


