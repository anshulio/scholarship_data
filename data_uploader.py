import firebase_admin
from firebase_admin import credentials,firestore
import os
import json

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
batch = db.batch()
fileCount = 0

for root,_,files in os.walk("./cleaned_data"):
    for file in files:
        data = ""
        path = os.path.join(root,file)
        with open(path,'r') as f:
            data = json.load(f)
        print(file)
        ref = db.collection("scholarship").document(data["schemeId"])
        batch.set(ref,data)

batch.commit()
        



