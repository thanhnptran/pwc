##################### FIRST PART #####################

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

################## END OF FIRST PART ##################

##################### SECOND PART #####################

bds_excel_path = r"C:\python\batdongsan\bds.xlsx"

def write_dict_to_excel(dictionary, file_path=bds_excel_path):
    suffix = '_’
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
    info_df = pd.DataFrame(dictionary).transpose().reset_index()
    first_key = list(dictionary.keys())[0]
    dicts = [element for element in list(info[first_key].keys()) if isinstance(info[first_key][element], dict)]
    if len(dicts) > 0:
        for idx, d in enumerate(dicts):
            flat_df = pd.json_normalize(info_df[d])
            info_df = info_df.join(flat_df,rsuffix=suffix*(idx+1))
    info_df = info_df.map(lambda x: ILLEGAL_CHARACTERS_RE.sub(r'', x) if isinstance(x, str) else x)
    info_df.to_excel(file_path,index=False)
    print(fr'Done! Check output excel file at {file_path}')
    return

info = {} # this is a dictionary
for idx, url in enumerate(url_list):
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH,"//div[contains(@class,'re__project-toogle-box')]")))
    project_name = driver.find_element(By.XPATH,"//h1[@class='re__project-name']").get_attribute('innerHTML')
    project_address = driver.find_element(By.XPATH,"//div[@class='re__project-address']").text.replace(". Xem bản đồ",'')
    items_html = driver.find_elements(By.XPATH,"//div[contains(@class,'js__project-box-info')]//div[@class='re__project-box-item']")
    
    details = {}
    for item in items_html:
        item_label = item.find_element(By.XPATH,"./label").get_attribute("innerHTML")
        details[item_label] = item.find_element(By.XPATH,"./span").get_attribute("innerHTML")

    info[idx] = {
        'url': url,
        'project_name': project_name,
        'project_address': project_address,
        'details': details
    }
    
    driver.quit()
    print(f"Done {idx}")

write_dict_to_excel(info)

################## END OF SECOND PART ##################
