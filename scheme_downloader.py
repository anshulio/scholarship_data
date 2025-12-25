import os
import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urlparse
base_url =  "https://api.myscheme.gov.in/search/v6/schemes"
headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36",
    "Origin": "https://www.myscheme.gov.in",
    "Referer": "https://www.myscheme.gov.in/",
    "x-api-key": "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc"
}
filters = [
    {"identifier": "isStudent", "value": "Yes"},
    {"identifier": "schemeCategory", "value": "Education & Learning"}
]
x = 0
data_packed = []
size = 10
skipped = 0
offset = 0
total_schemes = 325
pages = ["faqs?lang=en","documents?lang=en"]
while len(data_packed)<total_schemes:
    params = {
        "lang": "en",
        "q": json.dumps(filters),
        "keyword": "",
        "sort": "",
        "from": offset,
        "size": size
    }
    response = requests.get(base_url,headers=headers,params=params)
    data = response.json()
    if data['statusCode'] != 200:
        print("Error Occured")
        continue
    items = data["data"]["hits"]["items"]
    if not items:
        continue
    print(len(items))
    for item in items:
        slug = item["fields"]["slug"]
        data_packed.append(slug)
        print(f"Fetched {len(items)} schemes | Total so far {len(data_packed)}") 
        time.sleep(.1)
    offset += size

for prog in data_packed:
    url = f"https://api.myscheme.gov.in/schemes/v6/public/schemes?slug={prog}&lang=en"
    response = requests.get(url,headers=headers)
    if response.status_code != 200:
        print("Error occured",response.status_code)
        continue
    path = os.path.join("data",prog)
    os.makedirs(path,exist_ok=True)
    id = response.json()["data"]["_id"]
    with open(os.path.join(path,"scheme.json"),"w") as f:
        json.dump(response.json(),f)
    for i in range(len(pages)):
        url = f"https://api.myscheme.gov.in/schemes/v6/public/schemes/{id}/{pages[i]}"
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                skipped += 1
                continue
            data = res.json()
            path = urlparse(url)
            fileName = os.path.basename(path.path)
            with open(os.path.join("data",prog,fileName+".json"),"w") as f:
                json.dump(data,f)
            time.sleep(.1)
        except:
            print("Skipped",skipped,"files")

    x += 1
    print(x,"scheme captured")
