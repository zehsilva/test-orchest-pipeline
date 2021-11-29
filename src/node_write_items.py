import orchest
from pyclarify import SignalInfo, DataFrame
from pyclarify import APIClient
client = APIClient("./clarify-credentials.json")

inputs = orchest.get_inputs()
clarify_vars = []
if "clfy_dict" in inputs.keys():
    clarify_vars=list(inputs["clfy_dict"].keys())
    inputs = inputs["clfy_dict"]

for name in clarify_vars:
    new_signal_name = inputs[name]["name"]
    new_signal_id = name
    labels = inputs[name]['labels']
    args = { "name" : new_signal_name, "description" : f"Orchest data for {new_signal_name}",
                "labels" : labels }
    if "kwargs" in inputs[name].keys():
        args.update(inputs[name]["kargs"])

    metadata = SignalInfo(**args)
    
    save_signal_request = { 
        "inputs": {
            new_signal_id : metadata
            },
        "createOnly" : False #False = create new signal if none with the id exists, True = update existing signal
    }
    response = client.save_signals( save_signal_request )

    times = inputs[name]['times']
    series = {new_signal_id : inputs[name]['series']}
    new_df = DataFrame(times=times, series=series)
    response = client.insert(new_df)
    print(response)
    orchest.output(response, "insert_"+name)