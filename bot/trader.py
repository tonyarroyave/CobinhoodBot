'''
    TODO:
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
import various_functions as vf

# Let's open our holder
cup = 'cup_holder.json'
with open(cup) as f:
    holder = json.load(f)

strategy = holder['strategy']

if strategy == "long":
    # We are facing an uptrend but let's see if we are not already riding it
    # Easiest way to know is by checking our USDT balance
    balance_USDT = float(Cobi.get_USDT_balance())
    if (balance_USDT > 0):
        # We do have USDT to spend
        print('USDT: {}'.format(balance_USDT))
        # Here we should check if we are going to buy right after selling
        # But it will be added later on
        # Right now let's just make an order
        print('Placing buy order...')
        price_BTC = Cobi.get_ask_price(Cobi.basic_trading_pairs_ids[0])
        quantity = balance_USDT/price_BTC['price']
        quantity_r = quantity.quantize(decimal.Decimal(
            '.00000001'), rounding=decimal.ROUND_DOWN)
        order_response = Cobi.place_market_buy(
            Cobi.basic_trading_pairs_ids[0], quantity_r)
        print(order_response)
        # TODO: log in cup holder

    elif (Cobi.active_buy_orders(Cobi.basic_trading_pairs_ids[0])):
        print("We are waiting for a buy order to be made...")
        # TODO: Timer
    else:
        print("Must likely we bought everything we can... let's hold")
        holder['trader'] = "holding"

if strategy == "short":
    balance_BTC = float(Cobi.get_BTC_balance())
    if (balance_BTC > 0):
        print('BTC: {}'.format(balance_BTC))
        print('Placing sell order...')
        quantity = balance_BTC
        quantity_r = quantity.quantize(decimal.Decimal(
            '.00000001'), rounding=decimal.ROUND_DOWN)
        order_response = Cobi.place_market_sell(
            Cobi.basic_trading_pairs_ids[0], quantity_r)
        print(order_response)
        # TODO: log in cup holder

    elif (Cobi.active_sell_orders(Cobi.basic_trading_pairs_ids[0])):
        print("We are waiting for a sell order to be made...")
        # TODO: Timer
    else:
        print("Must likely we sold everything we can... let's hold")
        holder['trader'] = "holding"

print('Logging balances...')
vf.log_balances(float(Cobi.get_BTC_balance()), float(Cobi.get_USDT_balance()))

# Rewrite the cup holder file
with open(cup, 'w') as outfile:
    json.dump(holder, outfile)
