import websocket
import json
import time
import hashlib
import sys
from multiprocessing import Process, Manager
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_url = 'mysql+pymysql://root:@localhost/okcoin_future'

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()

manager = Manager()
shared_dict = manager.dict()
shared_dict['last_ping_time'] = time.time()
shared_dict['last_check_time'] = time.time()

ping_process = None
checker_process = None

class FutureIndex(Base):
    __tablename__ = 'future_index'
    timestamp = sa.Column(sa.BigInteger, primary_key=True)
    value = sa.Column(sa.Float, nullable=False)

    def __init__(self, data):
        self.value = data.get('futureIndex')
        self.timestamp = data.get('timestamp')

class FutureTrade(Base):
    __tablename__ = 'future_trade'
    trade_id = sa.Column(sa.BigInteger, primary_key=True)
    price = sa.Column(sa.Float, nullable=False)
    amount = sa.Column(sa.Integer, nullable=False)
    timestamp = sa.Column(sa.Integer, nullable=False)
    trade_type = sa.Column(sa.SmallInteger, nullable=False)
    contract_type = sa.Column(sa.SmallInteger, nullable=False)

    def __init__(self, trade_pair, contract_type):
        self.trade_id = int(trade_pair[0])
        self.price = float(trade_pair[1])
        self.amount = int(float(trade_pair[2]))
        now = datetime.now()
        time_offset = datetime.strptime(trade_pair[3], '%H:%M:%S')
        self.timestamp = int(time_offset.replace(year=now.year, month=now.month, day=now.day).timestamp())
        self.trade_type = 1 if trade_pair[4] == 'bid' else 2
        self.contract_type = contract_type

class FutureKline1min(Base):
    __tablename__ = 'future_kline_1min'
    timestamp = sa.Column(sa.Integer, primary_key=True)
    open = sa.Column(sa.Float, nullable=False)
    high = sa.Column(sa.Float, nullable=False)
    low = sa.Column(sa.Float, nullable=False)
    close = sa.Column(sa.Float, nullable=False)
    volume = sa.Column(sa.Integer, nullable=False)
    volume_btc = sa.Column(sa.Float, nullable=False)

    def __init__(self, pair, channel):
        if channel == 'ok_sub_futureusd_btc_kline_this_week_1min':
            time_offset = 1
        elif channel == 'ok_sub_futureusd_btc_kline_next_week_1min':
            time_offset = 2
        elif channel == 'ok_sub_futureusd_btc_kline_quarter_1min':
            time_offset = 4
        else:
            time_offset = 0
        self.timestamp = int(pair[0]) / 1000 + time_offset
        self.open = float(pair[1])
        self.high = float(pair[2])
        self.low = float(pair[3])
        self.close = float(pair[4])
        self.volume = int(pair[5])
        self.volume_btc = float(pair[6])

class FutureTick(Base):
    __tablename__ = 'future_tick'
    timestamp = sa.Column(sa.BigInteger, primary_key=True)
    low = sa.Column(sa.Float, nullable=False)
    buy = sa.Column(sa.Float, nullable=False)
    last = sa.Column(sa.Float, nullable=False)
    sell = sa.Column(sa.Float, nullable=False)
    high = sa.Column(sa.Float, nullable=False)
    volume = sa.Column(sa.Integer, nullable=False)

    def __init__(self, data, channel):
        if channel == 'ok_sub_futureusd_btc_ticker_this_week':
            time_offset = 1
        elif channel == 'ok_sub_futureusd_btc_ticker_next_week':
            time_offset = 2
        elif channel == 'ok_sub_futureusd_btc_ticker_quarter':
            time_offset = 4
        else:
            time_offset = 0

        self.timestamp = int(time.time() * 10000) * 10 + time_offset
        self.low = float(data.get('low'))
        self.buy = float(data.get('buy'))
        self.last = float(data.get('last'))
        self.sell = float(data.get('sell'))
        self.high = float(data.get('high'))
        self.volume = float(data.get('vol'))

def log(*args, **kargs):
    print(datetime.now().strftime('[%Y/%m/%d %H:%M:%S]'), *args, **kargs)

def ping(ws, shared_dict):
    while True:
        time_pass = time.time() - shared_dict['last_ping_time']
        if time_pass > 20:
            log('Not got pong for 20 seconds, exit process')
            ws.close()
            break
        elif time_pass > 10:
            ws.send("{'event':'ping'}")
        time.sleep(1)

def check(ws, shared_dict):
    # Start check after 30 seconds
    start_time = int(time.time())
    time.sleep(30)

    while True:
        now = int(time.time())
        time_pass = now - shared_dict['last_check_time']

        session = Session()

        last_future_index_timestamp = session.query(FutureIndex.timestamp)\
            .order_by(FutureIndex.timestamp.desc()).first()[0]
        last_future_trade_timestamp = session.query(FutureTrade.timestamp)\
            .order_by(FutureTrade.timestamp.desc()).first()[0]
        last_future_tick_timestamp = session.query(FutureTick.timestamp)\
            .order_by(FutureTick.timestamp.desc()).first()[0]
        num_of_last_hour_future_kline = session.query(FutureKline1min.timestamp)\
            .filter(FutureKline1min.timestamp > now - 3600).count()

        should_exit = False
        if now - last_future_index_timestamp / 1000 > 60:
            should_exit = True
        if now - last_future_trade_timestamp > 60:
            should_exit = True
        if now - last_future_tick_timestamp / 100000 > 60:
            should_exit = True
        if num_of_last_hour_future_kline < min(177, (now - start_time) / 20):
            should_exit = True

        session.close()

        if should_exit:
            ws.close()
            break

        shared_dict['last_check_time'] = now
        time.sleep(30)

def on_message(ws, messages):
    messages = json.loads(messages)
    if type(messages) == dict and messages.get('event') == 'pong':
        shared_dict['last_ping_time'] = time.time()
        return

    for message in messages:
        try:
            channel = message.get('channel')
            subscribe_success = message.get('success')
            if subscribe_success:
                continue

            if channel == 'ok_sub_futureusd_btc_index':
                data = message.get('data')
                if not data:
                    continue

                # Save to database
                session = Session()
                future_index = FutureIndex(data)
                session.merge(future_index)
                session.commit()
                session.close()

            elif channel[:27] == 'ok_sub_futureusd_btc_trade_':
                trade_pairs = message.get('data')
                if not trade_pairs:
                    continue
                if channel == 'ok_sub_futureusd_btc_trade_this_week':
                    contract_type = 1
                elif channel == 'ok_sub_futureusd_btc_trade_next_week':
                    contract_type = 2
                elif channel == 'ok_sub_futureusd_btc_trade_quarter':
                    contract_type = 3

                # Save to database
                session = Session()

                for trade_pair in trade_pairs:
                    if len(trade_pair) != 5:
                        log('Wrong trade', trade_pair, file=sys.stderr)
                        continue

                    future_trade = FutureTrade(trade_pair, contract_type)
                    session.merge(future_trade)
                session.commit()
                session.close()
            elif channel[:27] == 'ok_sub_futureusd_btc_kline_':
                kline_pairs = message.get('data')
                if not kline_pairs:
                    continue

                if type(kline_pairs[0]) == int:
                    kline_pairs = [kline_pairs]

                # Save to database
                session = Session()
                for kline_pair in kline_pairs:
                    if len(kline_pair) != 7:
                        log('Wrong kline', kline_pair, file=sys.stderr)
                        continue
                    future_kline_1min = FutureKline1min(kline_pair, channel)
                    session.merge(future_kline_1min)
                session.commit()
                session.close()
            elif channel[:28] == 'ok_sub_futureusd_btc_ticker_':
                data = message.get('data')
                if not data:
                    continue

                # Save to database
                session = Session()
                future_tick = FutureTick(data, channel)
                session.merge(future_tick)
                session.commit()
                session.close()
            else:
                log('Get unhandled channel', channel, file=sys.stderr)

        except Exception as e:
            log(e, file=sys.stderr)
            pass

def on_error(ws, error):
    log('error', error, file=sys.stderr)

def on_close(ws):
    global ping_process
    global checker_process
    if ping_process:
        ping_process.join(3)
    if checker_process:
        checker_process.join(3)
    log("### closed ###")

def on_open(ws):
    # Index
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_index'}")

    # Trades
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_trade_this_week'}")
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_trade_next_week'}")
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_trade_quarter'}")

    # Klines
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_kline_this_week_1min'}")
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_kline_next_week_1min'}")
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_kline_quarter_1min'}")

    # Ticker
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_ticker_this_week'}")
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_ticker_next_week'}")
    ws.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_ticker_quarter'}")

    # Health Beat
    global ping_process
    ping_process = Process(target=ping, args=(ws, shared_dict))
    ping_process.start()

    # Checker Process
    global checker_process
    checker_process = Process(target=check, args=(ws, shared_dict))
    checker_process.start()


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://real.okcoin.com:10440/websocket/okcoinapi",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    ws.run_forever()
