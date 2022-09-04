#import libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#changing chromedriver default options
options = Options()
options.headless = False
#options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('window-size=1920x1080') #Headless = True

web = 'https://www.betfair.com/sport/inplay'
#web = 'https://sports.tipico.de/en/live/soccer'
#path = '/Users/.../chromedriver' #introduce your file's path inside '...'
path = "C:\\Users\\hhsomek\\Downloads\\selenium\\chromedriver.exe"

#execute chromedriver with edited options
driver = webdriver.Chrome(executable_path = path, options=options)
driver.get(web)
#driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
#time.sleep(3)

#Make ChromeDriver click a button
#option 1
accept = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))


#option 2
#time.sleep(4)
#accept = driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]')
