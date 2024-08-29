from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time, re

driver_path = r"C:\Tools\chromedriver-win64\chromedriver.exe" # remember to change to your local file path 
service = Service(executable_path = driver_path)
driver = webdriver.Chrome(service=service)

landing_page = "https://batdongsan.com.vn/du-an-bat-dong-san-quan-2" 
driver.get(landing_page)
WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH,"//div[@class='re__prj-list-full']")))

url_list = [each.get_attribute('href') for each in driver.find_elements(By.XPATH,"//a[@tracking-id='project-card-plp']")]

url_path = r"C:\python\batdongsan\url_list.txt" # remember to change to your local file path 
with open(url_path, 'w') as file:    
    file.write('\n'.join(url_list))

driver.quit()
