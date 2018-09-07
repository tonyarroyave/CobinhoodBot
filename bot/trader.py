'''
    TODO:
    Get the strategy -> write strategy file
    get the balance -> balance functions
    get the amount to play
    place orders if necessary
    periodically check if they where held
    log every succesful transaction on csv -> log everything
'''

'''
    Consider that our main coin is USDT and we want to grow the amount of USDT
    Buy calls are to buy BTC because is low
    Sell calls are to get USDT back because BTC is high
'''

import json
import API as Cobi

# Let's open our holder

cup = 'cup_holder.json'
with open(cup) as f:
    holder = json.load(f)

strategy = holder['strategy']

if strategy != "hold":
    if strategy == "buy":
        USDT = Cobi.get_USDT_balance()
        if (USDT > 0):
            print(USDT)
        elif (Cobi.active_buy_orders()):
            print("We are waiting for a buy order to be made...")
        else:
            print("Must likely we bought everything we can... let's hold")
            holder['trader'] = "holding"

    if strategy == "sell":
        BTC = Cobi.get_BTC_balance()
        if (BTC > 0):
            print(BTC)
        elif (Cobi.active_sell_orders()):
            print("We are waiting for a sell order to be made...")
        else:
            print("Must likely we sold everything we can... let's hold")
            holder['trader'] = "holding"

else:
    print("Holding...")
    holder['trader'] = "holding"


# Rewrite the cup holder file

with open(cup, 'w') as outfile:
    json.dump(holder, outfile)
