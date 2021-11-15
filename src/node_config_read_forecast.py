import orchest

item_id = orchest.get_step_param("item_id")
days = orchest.get_step_param("lag_days")
lag = orchest.get_step_param("time_split") 
future = orchest.get_step_param("future") 
name = orchest.get_step_param("name") 

orchest.output({"item_id" : item_id, 
                "lag_days" : days,
                "time_split" : lag, "future" : future}, name=f"read_config_forecast_{name}")