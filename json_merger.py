import os
import json
from json_cleaner import load_multiple_json,generate_cleaned_json
for root,y,files in os.walk('./data'):
    finalPath = os.path.join(root,"final.json")
    if root == "./data":
        continue
    with open(finalPath,"a") as final:
        for file in files:
            fpath = os.path.join(root,file)
            with open(fpath,"r") as f:
                final.write((f.read()))
    raw_data = load_multiple_json(finalPath)
    cleaned_datas = generate_cleaned_json(raw_data)
    os.makedirs(os.path.join("cleaned_data"),exist_ok=True)
    with open(os.path.join("cleaned_data",cleaned_datas["schemeId"]+".json"),"w") as f:
        json.dump(cleaned_datas,f, indent=4, ensure_ascii=False)
        
    

                