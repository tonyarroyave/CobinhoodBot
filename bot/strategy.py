import pandas as pd
import numpy as np
import json
import various_functions as vf


def get_strategy(pm1, pm2, df):

    df['PM1'] = df['Average'].rolling(pm1).mean()
    df['PM2'] = df['Average'].rolling(pm2).mean()
    df.dropna(inplace=True)
    df = df[['Average', 'PM1', 'PM2']]
    df['Posicion'] = np.where(df['PM1'] > df['PM2'], 1, -1)
    _ = df['Posicion'].tail(1).copy()
    decision = _[0]

    return decision


cup = 'cup_holder.json'
with open(cup, 'r') as f:
    holder = json.load(f)

PM1, PM2 = vf.get_PMs()
strategy = get_strategy(PM1, PM2, vf.get_df())
if (strategy == 1):
    holder["strategy"] = "long"
    print("So the strategy is {}, it means 'Long'".format(strategy))
elif (strategy == -1):
    holder["strategy"] = "short"
    print("So the strategy is {}, it means 'Short'".format(strategy))
with open(cup, 'w') as outfile:
    json.dump(holder, outfile)
