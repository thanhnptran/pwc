import pandas as pd
import requests, time
from datetime import datetime, timedelta

endpoint = 'https://bingw.jasonzeng.dev'
headers = {
    'content-type': 'application/json',
    'accept': 'application/json'
}

def save_images(fromdate, todate, folder_path):
    start_date = datetime.strptime(fromdate,'%Y%m%d')
    end_date = datetime.strptime(todate,'%Y%m%d')
    date_range = pd.date_range(start_date,end_date-timedelta(days=1),freq='d').strftime('%Y%m%d').tolist()
    
    for date in date_range:
        params = {
            'resolution': 'UHD',
            'format': 'json',
            'date': f'{date}'
        }
        r = requests.get(endpoint,headers=headers,params=params)
        result = r.json()

        img_data = requests.get(result['url'], verify=False, stream=True)
        with open(fr'{folder_path}\{date}.jpg', 'wb') as handler:
            handler.write(img_data.content)
        print(f'Done {date}')
        time.sleep(2)

img_folder_path = r"C:\python\images" # remember to change to your local file path 
save_images('20240801', '20240811', img_folder_path)
