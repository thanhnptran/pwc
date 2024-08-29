import requests

endpoint = 'https://bingw.jasonzeng.dev'
headers_json = {
    'content-type': 'application/json',
    'accept': 'application/json'
}
params_json = {
    'resolution': 'UHD',
    'format': 'json',
    'date': '20230115'
}

r = requests.get(endpoint, headers=headers_json, params=params_json)
result = r.json()

result['url']

img_data = requests.get(result['url'], verify=False, stream=True)
file_path = r"C:\python\20230115.jpg" # remember to change to your local file path 
with open(file_path, 'wb') as handler:
    handler.write(img_data.content)
