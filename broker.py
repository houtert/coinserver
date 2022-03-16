import logging

from python_bitvavo_api.bitvavo import Bitvavo

from secret import *

logger = logging.getLogger()


class Broker:
    def __init__(self, brokername="bitvavo"):
        self.brokername = brokername.lower()
        if self.brokername == "bitvavo":
            self.broker = Bitvavo({
                'APIKEY': BITVAVOAPIKEY,
                'APISECRET': BITVAVOSECRET,
                'RESTURL': 'https://api.bitvavo.com/v2',
                'WSURL': 'wss://ws.bitvavo.com/v2/',
                'ACCESSWINDOW': 60000,
                'DEBUGGING': False
            })
            self.assets = self.get_assets()
        else:
            logger.warning("Broker.init : {} not supported yet!!!".format(self.brokername))

    def __repr__(self):
        return "Broker object, name : {}".format(self.brokername)

    def get_asset(self, symbol):
        coin = symbol.upper()
        result = {}
        for asset in self.assets:
            if asset['symbol'] == coin:
                result = asset
        return result

    def get_assets(self):
        if self.brokername == 'bitvavo':
            assets = self.broker.assets({})
        else:
            assets = []
            logger.warning("Broker.get_assets : {} not supported yet!!!".format(self.brokername))
        return assets

    def get_symbols(self):
        symbols = []
        if self.brokername == 'bitvavo':
            for asset in self.assets:
                symbols.append(asset['symbol'])
        else:
            logger.warning("Broker.get_symbols : {} not supported yet!!!".format(self.brokername))
        return symbols

    def get_prices(self):
        result = {}
        if self.brokername == 'bitvavo':
            ticker = self.broker.tickerPrice({})
            for item in ticker:
                symbol = item['market'][:-4]
                if item['market'][-4:] == '-EUR':
                    value = item['price']
                    result[symbol] = float(value)
        else:
            logger.warning("Broker.get_prices : {} not supported yet!!!".format(self.brokername))

        return result

    def get_price(self, symbol):
        prices = self.get_prices()
        return prices[symbol]

    def get_balance(self):
        result = []
        euros = 0.0
        if self.brokername == 'bitvavo':
            coins = self.broker.balance({})
            for coin in coins:
                amount = float(coin['available'])
                if coin['symbol'] == 'EUR':
                    euros = amount
                else:
                    if amount > 0:
                        entry = {"symbol": coin['symbol'], "amount": amount}
                        result.append(entry)
        else:
            logger.warning("Broker.get_balance : {} not supported yet!!!".format(self.brokername))

        return euros, result

    def get_last_candles(self, symbol):
        pair = symbol.upper() + "-EUR"

        limit = self.broker.getRemainingLimit()
        if limit > 0:
            candles = self.broker.candles(pair, '1h', {})
            for candle in candles:
                candle[0] = candle[0] / 1000

        return candles
