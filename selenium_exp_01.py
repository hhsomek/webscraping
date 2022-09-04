from selenium import webdriver
import time

driver_path = "C:\\Users\\hhsomek\\Downloads\\selenium\\chromedriver"
browser = webdriver.Chrome(executable_path = driver_path)

browser.get("https://www.youtube.com/")
time.sleep(5)
browser.quit()