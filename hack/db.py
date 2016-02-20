from pymongo import MongoClient
from hack import config
import influxdb
import gevent
import logging

def init_mongodb():
    mongo_connected = False
    while not mongo_connected:
        try:
            MONGO = MongoClient(config.MONGO_HOST, config.MONGO_PORT, use_greenlets=True, max_pool_size=10)
            mongo_connected = True
        except Exception as e:
            logging.info("MongoDB not connected")
            logging.error(e)
            gevent.sleep(1)

    return MONGO

def init_influxdb():
    influx_connected = False
    while not influx_connected:
        try:
            INFLUX = influxdb.InfluxDBClient(
                config.INFLUX_HOST,
                config.INFLUX_PORT,
                config.INFLUX_USER,
                config.INFLUX_PASSWORD,
                config.INFLUX_DATABASE,
            )
            influx_connected = True
        except Exception as e:
            logging.info("Influxdb not connected")
            logging.error(e)
            gevent.sleep(1)

    return INFLUX

def create_shards(INFLUX):
    logging.info("Creating Influxdb database, retention policies and continuous queries")
    try:
        res = INFLUX.create_database(config.INFLUX_DATABASE)
    except Exception as e:
        logging.error(e)
