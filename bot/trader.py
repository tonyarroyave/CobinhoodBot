'''
    TODO:
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
import decimal

# Let's open our holder
cup = 'cup_holder.json'
with open(cup) as f:
    holder = json.load(f)

strategy = holder['strategy']

if strategy == "long":
    # We are facing an uptrend but let's see if we are not already riding it
    # Easiest way to know is by checking our USDT balance
    balance_USDT = Cobi.get_USDT_balance()
    # LOG USDT BALANCE
    if (balance_USDT > 0):
        # We do have USDT to spend
        print('USDT: {}'.format(USDT))
        # Here we should check if we are going to buy right after selling
        # But it will be added later on
        # Right now let's just make an order
        print('Placing buy order...')
        price_USDT = Cobi.get_price_in_USDT('BTC')
        quantity = balance_USDT/price_USDT['price']
        quantity_r = quantity.quantize(decimal.Decimal(
            '.00000001'), rounding=decimal.ROUND_DOWN)
        order_response = Cobi.place_market_buy(
            Cobi.basic_trading_pairs_ids[0], quantity_r)
        print(order_response)

    elif (Cobi.active_buy_orders()):
        print("We are waiting for a buy order to be made...")
    else:
        print("Must likely we bought everything we can... let's hold")
        holder['trader'] = "holding"

if strategy == "short":
    BTC = Cobi.get_BTC_balance()
    if (BTC > 0):
        print(BTC)
    elif (Cobi.active_sell_orders()):
        print("We are waiting for a sell order to be made...")
    else:
        print("Must likely we sold everything we can... let's hold")
        holder['trader'] = "holding"

# Rewrite the cup holder file

with open(cup, 'w') as outfile:
    json.dump(holder, outfile)
