from cobinhood_api import Cobinhood
from Keys import *
import json
import requests

cob = Cobinhood(API_TOKEN=API_KEY)

basic_trading_pairs_ids = ["BTC-USDT"]   # this should grow with time


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
        "size": quantity
    }
    return cob.trade.post_orders(data)


def place_market_buy(pair_id, quantity):
    '''
    All data should be a string
    '''
    data = {
        "trading_pair_id": pair_id,
        "side": "bid",
        "type": "market",
        "size": quantity
    }
    return cob.trade.post_orders(data)


def place_limit_sell(pair_id, quantity, price):
    '''
    All data should be a string
    '''
    data = {
        "trading_pair_id": pair_id,
        "side": "ask",
        "type": "limit",
        "price": price,
        "size": quantity
    }
    return cob.trade.post_orders(data)


def place_limit_buy(pair_id, quantity, price):
    '''
    All data should be a string
    '''
    data = {
        "trading_pair_id": pair_id,
        "side": "bid",
        "type": "limit",
        "price": price,
        "size": quantity
    }
    return cob.trade.post_orders(data)
