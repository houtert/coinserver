import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from secret import USER, PASSWORD, PORT, HOST

logger = logging.getLogger()


class Coindb:
    def __init__(self, name='coinserver'):
        self.name = name
        self.coins = []
        self.engine = self.open_db()
        table = pd.read_sql_query("SHOW TABLES", self.engine)

        if len(table) > 0:
            self.coins = table['Tables_in_coinserver'].tolist()

    def open_db(self):
        engine = None
        connection = "mysql+pymysql://" + USER + ":" + PASSWORD + "@" + HOST + ":" + str(PORT) + "/" + self.name
        try:
            engine = create_engine(connection)
        except SQLAlchemyError as e:
            logging.error(" Coindb.create_engine : ", e)
            exit(1)
        return engine

    def is_valid(self, symbol):
        coin = symbol.upper()
        return coin in self.coins

    def get_candles(self, symbol, size=-1):
        coin = symbol.upper()
        result = None
        try:
            if coin in self.coins:
                if size == -1:
                    result = pd.read_sql('SELECT Time, Open, High, Low, Close, Volume FROM ' + coin + ' ORDER BY Time',
                                         self.engine)
                else:
                    result = pd.read_sql(
                        'SELECT Time, Open, High, Low, Close, Volume FROM ' + coin + ' ORDER BY Time DESC LIMIT ' + str(
                            size), self.engine)
                    result = result[::-1]
                    result.reset_index(inplace=True, drop=True)
                result['Time'] = result['Time'].dt.strftime("%Y-%m-%d %H:%M")
        except SQLAlchemyError as e:
            logging.error("Coinserver.get_prices : ", e)

        return result

    def get_prices(self, symbol, size=-1):
        coin = symbol.upper()
        result = None
        try:
            if coin in self.coins:
                if size == -1:
                    result = pd.read_sql('SELECT Time, Close as Price FROM ' + coin + ' ORDER BY Time', self.engine)
                else:
                    result = pd.read_sql(
                        'SELECT Time, Close as Price FROM ' + coin + ' ORDER BY Time DESC LIMIT ' + str(size),
                        self.engine)
                    result = result[::-1]
                    result.reset_index(inplace=True, drop=True)
                result['Time'] = result['Time'].dt.strftime("%Y-%m-%d %H:%M")
        except SQLAlchemyError as e:
            logging.error("Coinserver.get_prices : ", e)

        return result

    def get_price(self, symbol):
        result = 0.0
        coin = symbol.upper()
        prices = self.get_prices(coin, 1)
        if len(prices) > 0:
            result = "{:.2f}".format(prices.iloc[-1]['Price'])
        return (result)

    def get_coins(self):
        return self.coins

    def count_per_day(self, symbol):
        coin = symbol.upper()
        result = None
        try:
            if coin in self.coins:
                result = pd.read_sql("SELECT DATE(TIME) as 'Day', COUNT(*) AS 'Items' FROM " + coin +
                                     " GROUP BY DATE(TIME)", self.engine)
        except SQLAlchemyError as e:
            logging.error("Coinserver.count_per_day : ", e)

        result = result.set_index('Day')
        return result

    def get_last_datapoints(self, symbol, points=4):
        coin = symbol.upper()
        prices = self.get_prices(coin, points)

        return prices

    def get_size(self, symbol):
        coin = symbol.upper()
        count = 0
        try:
            if coin in self.coins:
                result = pd.read_sql('SELECT COUNT(*) AS "COUNT" FROM ' + coin, self.engine)
                count = result['COUNT'].iloc[0]
        except SQLAlchemyError as e:
            logging.error("Coindb.get_datapoints : ", e)

        return count

    def get_datapoints_by_date(self, symbol, date):
        coin = symbol.upper()
        try:
            if coin in self.coins:
                result = pd.read_sql("SELECT * FROM " + coin + " WHERE DATE(Time) LIKE '" + str(date) + "'",
                                     self.engine)
        except SQLAlchemyError as e:
            logging.error("Coindb.get_datapoints_by_date : ", e)

        return result

    def missing_days(self, symbol):
        coin = symbol.upper()
        values = self.count_per_day(coin)
        begin = values.index[0]
        end = values.index[-1]
        print(begin, end)
        all_days = pd.date_range(begin, end)
        values = values.reindex(all_days, fill_value=0)

        values = values[values['Items'] < 24]
        return values
