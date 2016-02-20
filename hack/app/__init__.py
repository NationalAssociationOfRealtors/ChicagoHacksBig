from flask import Flask, redirect, url_for, request, g
from flask.ext.session import Session
from hack import config
from hack import db
from slugify import slugify
import logging
import time

logging.basicConfig(level=config.LOG_LEVEL)

class App(Flask):

    def __init__(self):
        super(App, self).__init__(__name__)
        self.config.from_object('hack.config')
        logging.info("SERVER_NAME: {}".format(self.config['SERVER_NAME']))
        self.before_request(self.init_dbs)
        self.teardown_request(self.teardown)
        self.after_request(self.teardown)
        try:
            self.init_templates()
        except Exception as e:
            logging.exception(e)

    def init_templates(self):
        self.jinja_env.filters['slugify'] = slugify

    def teardown(self, exception):
        return exception

    def configure_dbs(self):
        influx = db.init_influxdb()
        db.create_shards(influx)

    def init_dbs(self):
        g.INFLUX = db.init_influxdb()
