"""
    Mr Charehei 2022-03-10
    CURD => create , update , read , delete strategies
    this file used in panel.py

    strategy name : name_symbol_timeframe_type
    example strategy name : opal_ADA-USDT_1hour_sell or opal_ADA-USDT_1hour_buy

"""
from redis import Redis 
import json


class Strategy:

    # save strategy on redis by broker and name

    # strategy = {
    #     "name": str,
    #     "condition": list(dict), : [{"p1": "close_price", "p2": "open_price", "rel": "gt"}]
    #     "duration": str,
    #     "time_frame": str,
    #     "symbol": str,
    #     "broker": str,
    #     "candle_count": int,
    #     "user_list": list
    # }

    fields = ["name", "condition", "duration", "time_frame", "symbol", "broker", "candle_count"]
    redis = Redis()

    def get_transactions(self, data: dict):
        data = self.redis.hgetall("%s_trx" % data["broker"])
        d = dict()
        if data:
            for key, value in data.items():
                d[key.decode()] = json.loads(value.decode())
            return d
        return None

    def strategy_by_broker(self, broker: str):
        data = self.redis.hgetall(broker)
        if data:
            return data
        else:
            raise Exception("no any strategy in ", broker)

    def strategy_by_user(self, email: str, broker: str):
        broker_strategies = self.strategy_by_broker(broker)
        strategy_list = list()
        for strategy in broker_strategies.values():
            strategy = json.loads(strategy)
            if email in strategy["user_list"]:
                strategy_list.append(strategy)
        return strategy_list

    def read_all(self, data: dict):
        key = data["broker"]
        data = self.redis.hgetall(key)
        d = dict()
        if data:
            for key, value in data.items():
                d[key.decode()] = json.loads(value.decode())
            return d
        return None

    def read(self, strategy_name: str, symbol: str, time_frame: str, broker: str):
        key = "%s_%s_%s" % (strategy_name, symbol, time_frame)
        strategy = self.redis.hget(broker, key)
        if strategy:
            return json.loads(strategy)
        return None

    def write(self, data: dict):
        strategy = dict()
        try:
            for field in self.fields:
                strategy[field] = data[field]
                del data[field]
        except Exception as error:
            raise Exception("data is invalid : %s" % error)

        if len(data.keys()) > 0:
            strategy.update(data)
            
        json_strategy = json.dumps(strategy)
        key = "%s_%s_%s" % (strategy["name"], strategy["symbol"], strategy["time_frame"])
        self.redis.hset(strategy["broker"], key, json_strategy)

    def delete(self, strategy_name: str, symbol: str, time_frame: str, broker: str):
        key = "%s_%s_%s" % (strategy_name, symbol, time_frame)
        self.redis.hdel(broker, key)

    def update(self, data: dict):
        self.delete(data["name"], data["symbol"], data["time_frame"], data["broker"])
        self.write(data)
