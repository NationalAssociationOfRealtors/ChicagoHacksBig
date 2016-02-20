from gevent import monkey
monkey.patch_all()

from werkzeug.wsgi import peek_path_info
from hack import config
from hack.app import App
from hack.controllers.geofences import geofence
import logging
logging.basicConfig(level=config.LOG_LEVEL)

def healthcheck(app, env):
    if peek_path_info(env) == "healthcheck":
        app.config['SERVER_NAME'] = None
    else:
        app.config['SERVER_NAME'] = config.SERVER_NAME

def create_app():
    logging.info("Initializing")
    _app = App()
    _app.register_blueprint(geofence)
    def app(env, start_response):
        #healthcheck(_app, env)
        return _app(env, start_response)

    logging.info("Running")
    return app

app = create_app()
