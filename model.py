import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

from broker import Broker

import logging

logger = logging.getLogger()

class Model:
    def __init__(self, database):
        self.db = database
        self.broker = Broker()

    def calc_performance(self, hour, model):
        scores = []
        gain = 0.0

        regressor = LinearRegression()

        for coin in self.db.coins:
            data = self.db.get_last_datapoints(coin, hour+1)
            price = self.broker.get_price(coin)

            timestr = datetime.now()
            item = {'Time': timestr, 'Price': price}
            data = data.append(item, ignore_index=True)

            if model == "LIN":
                data['log_return'] = np.log(data['Price'] / data['Price'].shift(1)).dropna()
                gain = np.exp(data['log_return'].sum())
            elif model == "REG":
                X = np.arange(hour+2, dtype=float).reshape(-1, 1)

                y = data['Price']
                y = y.div(y.iloc[0]).mul(100)
                y = y.values.reshape(-1, 1)

                regressor.fit(X, y)
                gain = float(regressor.coef_)
            else:
                logger.warning ("Model.calc_performance : unknown model "+model+"!!!")

            score = {'Coin' : coin.upper(), 'Gain' : round(gain, 2)}
            scores.append(score)

        scores.sort(key = lambda x: x['Gain'], reverse=True)
        return scores

    def get_performance (self, hour=4, max_coins=10, algorithm="LIN"):
        if max_coins > len(self.db.coins):
            number = len(self.db.coins)
        else:
            number = max_coins

        scores = self.calc_performance(hour, algorithm.upper())

        best = scores[:number]
        length = len(scores)
        worst = scores[length-number:]

        return best, worst