from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = webdriver.Chrome('C:/Users/asantamaria/chromedriver')

driver.get("https://it.tradingview.com/")

timeout = 5
try:
    element_present = EC.presence_of_element_located((By.XPATH, "(//*[name()='svg'])[6]"))
    WebDriverWait(driver, timeout).until(element_present)
except TimeoutException:
    print("Timed out waiting for page to load")

driver.find_element_by_xpath("(//*[name()='svg'])[6]").click()

try:
    element_present = EC.presence_of_element_located((By.XPATH, "(//div[contains(text(),'Accedi')])[1]"))
    WebDriverWait(driver, timeout).until(element_present)
except TimeoutException:
    print("Timed out waiting for page to load")

driver.find_element_by_xpath("(//div[contains(text(),'Accedi')])[1]").click()

try:
    element_present = EC.presence_of_element_located((By.XPATH, "(//span[@class='tv-signin-dialog__social tv-signin-dialog__toggle-email js-show-email'])[1]"))
    WebDriverWait(driver, timeout).until(element_present)
except TimeoutException:
    print("Timed out waiting for page to load")

driver.find_element_by_xpath("(//span[@class='tv-signin-dialog__social tv-signin-dialog__toggle-email js-show-email'])[1]").click()

try:
    element_present = EC.presence_of_element_located((By.CLASS_NAME, "tv-control-material-input__wrap"))
    WebDriverWait(driver, timeout).until(element_present)
except TimeoutException:
    print("Timed out waiting for page to load")

driver.find_element_by_name("username").send_keys("the_only_one@hotmail.it")

driver.find_element_by_name("password").send_keys("281289ale")
driver.find_element_by_class_name("tv-button__loader").click()

try:
    element_present = EC.presence_of_element_located((By.XPATH, "(//div[@data-name='alerts'])[1]"))
    WebDriverWait(driver, timeout).until(element_present)
except TimeoutException:
    print("Timed out waiting for page to load")

driver.find_element_by_xpath("(//div[@data-name='alerts'])[1]").click()




