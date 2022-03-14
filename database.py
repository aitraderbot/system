"""
    Mr Charehei 2022-03-10
    relation with database (mysql)
    managin assets and users
    all data for each broker is uniqe (each data in their database)
    TODO : access to database is denied
"""
from re import L
import mysql.connector


class DatabaseRouter:
    username = "trader"
    password = "pythonP@@123"
    host = "localhost"
    dbname = ""

    # create database for each broker (Binance,Coinex,Kucoin)

    def __init__(self, broker: str) -> None:
        self.dbname = broker
        self.db = None
        self.cursor = None

    def connect(self):
        self.db = mysql.connector.connect(user=self.username,
                                          password=self.password,
                                          host=self.host,
                                          database=self.dbname)
        self.cursor = self.db.cursor()

    def disconnect(self):
        self.db.close()
        self.cursor.close()

    def create_table_asset_strategy(self):
        query = "CREATE TABLE IF NOT EXISTS user_strategy_setting (email VARCHAR(200), strategy_name VARCHAR(200), " \
                "symbol VARCHAR(200), time_frame VARCHAR(200), amount int, value_type VARCHAR(200)) "
        self.cursor.execute(query)

    def create_table_user(self):
        query = "CREATE TABLE IF NOT EXISTS user (email VARCHAR(200), password VARCHAR(300), api_key VARCHAR(300), " \
                "secret_key VARCHAR(300), passphrase VARCHAR(300)) "
        self.cursor.execute(query)

    def read_asset_strategy(self, email: str, strategy_name: str, symbol: str, time_frame: str):
        query = "SELECT amount FROM user_strategy_setting WHERE email='%s' AND strategy_name='%s' AND symbol='%s' AND " \
                "time_frame='%s'" % (email, strategy_name, symbol, time_frame)
        self.connect()
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        data = {"amount": data[0][0]}
        self.disconnect()
        return data

    def write_asset_strategy(self, data: dict):
        # email, strategy_name, symbol, time_frame, amount, value_type
        self.connect()
        self.create_table_asset_strategy()
        query = "INSERT INTO user_strategy_setting VALUES ('%s', '%s', '%s', '%s', %s, '%s')" % (data["email"],
                                                                                                 data["strategy_name"],
                                                                                                 data["symbol"],
                                                                                                 data["time_frame"],
                                                                                                 data["amount"],
                                                                                                 data["value_type"])
        self.cursor.execute(query)
        self.db.commit()
        self.disconnect()

    def update_asset_strategy(self, data: dict):
        # make condition string make column string
        try:
            condition_key_list = ["email", "strategy_name", "symbol", "time_frame"]
            l = list()
            for ck in condition_key_list:
                s = "%s='%s'" % (ck, data[ck])
                l.append(s)
            condition_string = " AND ".join(l)
            column_string = "amount='%s' value_type='%s'" % (data["amount"], data["value_type"])
        except KeyError:
            raise Exception("invalid data")

        query = "UPDATE user_strategy_setting SET %s WHERE %s" % (column_string, condition_string)
        self.connect()
        self.cursor.execute(query)
        self.db.commit()
        self.disconnect()

    def read_user(self, email: str, password: str = ""):
        query = 'SELECT * FROM user WHERE email="%s"' % email
        if password:
            query += " password='%s'" % password
        self.connect()
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        self.disconnect()
        return data

    @staticmethod
    def get_query(data: dict):
        try:
            broker = data["broker"]
        except KeyError:
            raise Exception("broker not found in data")
        raw_query = "INSERT INTO user %s VALUES %s"
        if broker == "kucoin":
            str_user = "('%s', '%s', '%s', '%s', '%s')" % (
                data["email"], data["password"], data["api_key"], data["secret_key"], data["passphrase"])
            query = raw_query % ("(email, password, api_key, secret_key, passphrase)", str_user)
            return query
        elif broker == "coinex":
            str_user = "('%s', '%s', '%s', '%s')" % (
                data["email"], data["password"], data["api_key"], data["secret_key"])
            query = raw_query % ("(email, api_key, secret_key, passphrase)", str_user)
            return query

    def write_user(self, data: dict):
        # kucoin : email, api_key, secret_key, passphrase
        # coinex : email, api_key, secret_key
        self.create_table_user()
        query = self.get_query(data)
        self.connect()
        self.cursor.execute(query)
        self.db.commit()
        self.disconnect()

    def update_user(self):
        pass

    def delete_user(self):
        pass
