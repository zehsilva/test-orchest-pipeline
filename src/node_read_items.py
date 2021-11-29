from datetime import datetime, timedelta
from pyclarify import APIClient
import orchest
import pandas as pd
import numpy as np



client = APIClient("./clarify-credentials.json")

inputs = orchest.get_inputs()
invars = [x for x in inputs.keys() if x.startswith("read_config")]

output_dict={}

for name in invars:
    
    item_id = inputs[name]['item_id']
    lag= inputs[name]['lag_days']


    data_params = {
      "items": {
        "include": True,
        "filter": {
          "id": {
            "$in": [
              item_id
            ]
          }
        }
      },
      "data": {
        "include": True,
        "notBefore": (datetime.now() - timedelta(days=lag)).astimezone().isoformat() #starting from 
      }
    }


    response = client.select_items(data_params)
    
    
orchest.output(output_dict, "clfy_read_result")

    
    

    
    