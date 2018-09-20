from cobinhood_api import Cobinhood
from Keys import *
import json
import requests

cob = Cobinhood(API_TOKEN=API_KEY)

basic_trading_pairs_ids = ["BTC-USDT"]   # this should grow with time


def active_buy_orders(pair_id):
    orders = cob.trading.get_orders()
    active = False
    if (orders['success'] == True):
        ord_array = orders['result']['orders']
        if len(ord_array) > 0:
            for each in ord_array:
                if (each['side'] == 'bid') and (each['trading_pair_id'] == pair_id):
                    active = True
                    return active
    else:
        raise Exception('Could not get orders!')
    return active


def active_sell_orders(pair_id):
    orders = cob.trading.get_orders()
    active = False
    if (orders['success'] == True):
        ord_array = orders['result']['orders']
        if len(ord_array) > 0:
            for each in ord_array:
                if (each['side'] == 'ask') and (each['trading_pair_id'] == pair_id):
                    active = True
                    return active
    else:
        raise Exception('Could not get orders!')
    return active


def get_USDT_balance():
    balances = cob.wallet.get_balances()
    found = False
    if (balances['success'] == True):
        bal_array = balances['result']['balances']
        for each in bal_array:
            if (each['currency'] == 'USDT'):
                found = True
                return each['total']
        if found == False:
            return 0.0
    else:
        raise Exception('Could not get USDT balances!')


def get_BTC_balance():
    balances = cob.wallet.get_balances()
    found = False
    if (balances['success'] == True):
        bal_array = balances['result']['balances']
        for each in bal_array:
            if (each['currency'] == 'BTC'):
                found = True
                return each['total']
        if found == False:
            return 0.0
    else:
        raise Exception('Could not get BTC balances!')


def get_ask_price(pair_id):
    response = requests.get(
        'https://api.cobinhood.com/v1/market/tickers/{}'.format(pair_id))
    if (response.status_code):
        info = json.loads(response.text)
        if (info['success']):
            return {'timestamp': info['result']['ticker']['timestamp'], 'price': info['result']['ticker']['lowest_ask']}
        else:
            print('API did not respond')
    else:
        print('Error connecting to API')


def get_bid_price(pair_id):
    response = requests.get(
        'https://api.cobinhood.com/v1/market/tickers/{}'.format(pair_id))
    if (response.status_code):
        info = json.loads(response.text)
        if (info['success']):
            return {'timestamp': info['result']['ticker']['timestamp'], 'price': info['result']['ticker']['highest_bid']}
        else:
            print('API did not respond')
    else:
        print('Error connecting to API')


def get_price_in_USDT(coin):
    '''
    Coin name must be it's acronym in a String format
    '''
    response = requests.get(
        'https://api.cobinhood.com/v1/market/tickers/{}-USDT'.format(coin))
    if (response.status_code):
        info = json.loads(response.text)
        if (info['success']):
            return {'timestamp': info['result']['ticker']['timestamp'], 'price': info['result']['ticker']['last_trade_price']}
        else:
            print('API did not respond')
    else:
        print('Error connecting to API')


def get_price_in_BTC(coin):
    '''
    Coin name must be it's acronym in a String format
    '''
    response = requests.get(
        'https://api.cobinhood.com/v1/market/tickers/{}-BTC'.format(coin))
    if (response.status_code):
        info = json.loads(response.text)
        if (info['success']):
            return {'timestamp': info['result']['ticker']['timestamp'], 'price': info['result']['ticker']['last_trade_price']}
        else:
            print('API did not respond')
    else:
        print('Error connecting to API')


def place_market_sell(pair_id, quantity):
    '''
    All data should be a string
    '''
    data = {
        "trading_pair_id": pair_id,
        "side": "ask",
        "type": "market",
        "size": str(quantity)
    }
    return cob.trading.post_orders(data)


def place_market_buy(pair_id, quantity):
    '''
    All data should be a string
    '''
    data = {
        "trading_pair_id": pair_id,
        "side": "bid",
        "type": "market",
        "size": str(quantity)
    }
    return cob.trading.post_orders(data)


def place_limit_sell(pair_id, quantity, price):
    '''
    All data should be a string
    '''
    data = {
        "trading_pair_id": pair_id,
        "side": "ask",
        "type": "limit",
        "price": price,
        "size": str(quantity)
    }
    return cob.trading.post_orders(data)


def place_limit_buy(pair_id, quantity, price):
    '''
    All data should be a string
    '''
    data = {
        "trading_pair_id": pair_id,
        "side": "bid",
        "type": "limit",
        "price": price,
        "size": str(quantity)
    }
    return cob.trading.post_orders(data)
