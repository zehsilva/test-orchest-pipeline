from datetime import datetime, timedelta
from pyclarify import APIClient
import orchest
import pandas as pd
import numpy as np
from merlion.utils import TimeSeries
from merlion.models.forecast.prophet import Prophet, ProphetConfig
from merlion.transform.base import Identity


def pipeline_data(times, values, new_id,new_name, original_id, original_name):
    labels = {"source":["Orchest pipelines"], "original_id":[original_id]}
    var_name = "clfy_"+new_id
    
    data =  {
            "name" : new_name,
            "labels" : labels,
            "times" : times,
            "series" : values,
            "kargs" : {"sourceType" : "prediction",
                        "data-source": ["Orchest"],
                        "description" : f"Forecast for {original_name}"
                      }
    }
    return {var_name : data }

def generate_future_timestamps(n_future, timestamps, start):
    deltas = [x-timestamps[0] for x in timestamps]
    avg_delta=np.mean(deltas)
    future = [(i+1)*avg_delta+start for i in range(n_future)]
    return future


client = APIClient("./clarify-credentials.json")

inputs = orchest.get_inputs()
invars = [x for x in inputs.keys() if x.startswith("read_config_forecast")]
print(invars)

output_dict={}

for name in invars:
    
    item_id = inputs[name]['item_id']
    days = inputs[name]['lag_days']
    test_lag = inputs[name]['time_split']
    future = inputs[name]['future']

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
        "notBefore": (datetime.now() - timedelta(days=days)).astimezone().isoformat()
      }
    }



    response = client.select_items(data_params)
    signal_name = list(response.result.items.values())[0].name
    print(f"Name {signal_name} and id {item_id}")
    times = response.result.data.times
    series = response.result.data.series
    df = pd.DataFrame(series)
    df.index = [time.replace(tzinfo=None) for time in times]
    if len(times) > 0:
        tzinfo = times[0].tzinfo
    
    test_data = TimeSeries.from_pd(df[-test_lag:])
    train_data = TimeSeries.from_pd(df[0:-test_lag])
    config = ProphetConfig(max_forecast_steps=test_lag, add_seasonality="auto", transform=Identity())
    model  = Prophet(config)
    model.train(train_data=train_data)
    test_times =  test_data.time_stamps
    if future > 0:
       test_times=test_times+generate_future_timestamps(future, test_data.time_stamps, start=test_data.time_stamps[-1])
    test_pred, test_err = model.forecast(time_stamps=test_times)

    col = test_pred.names[0]
    col_err = test_err.names[0]
    forecast_name=col+"_pred"
    forecast_name_upper=col+"_upper"
    forecast_name_lower=col+"_lower"
    
    forecast_values = test_pred.univariates[col].values
    forecast_upper_values= [x+y for x,y in zip(test_pred.univariates[col].values, test_err.univariates[col_err].values)]
    forecast_lower_values= [x-y for x,y in zip(test_pred.univariates[col].values, test_err.univariates[col_err].values)]

    output_dict.update(pipeline_data(test_pred.time_stamps,forecast_values, forecast_name, f"Forecast {signal_name}", col,  signal_name ))
    output_dict.update(pipeline_data(test_err.time_stamps,forecast_upper_values, forecast_name_upper, f"Forecast {signal_name} upper bound", col,  signal_name ))
    output_dict.update(pipeline_data(test_err.time_stamps,forecast_lower_values, forecast_name_lower, f"Forecast {signal_name} lower bound", col,  signal_name ))
    
orchest.output(output_dict, "clfy_dict")

    
    

    
    