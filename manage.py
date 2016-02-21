from flask import Flask, url_for
from flask.ext.script import Manager, Command, Option
from hack import config
from hack.app import App
from hack import db
from datetime import datetime
import logging
import csv

logging.basicConfig(level=logging.INFO)
app = App()
manager = Manager(app)

class LoadData(Command):

    def run(self):
        influx = db.init_influxdb()
        db.create_shards(influx)
        with open('data/DoStuff_Visits_02-18-16_02-19-16.csv') as csvfile:
            rows = csv.reader(csvfile, delimiter=",")
            next(rows)
            points = []
            for r in rows:
                visit_id, start, end, place_id, place_name, v1_user, v2_user, platform, visits, dwell_time, url, city, phone, address, lat, lng, metro_id, metro_title = r
                start = datetime.strptime(start, "%m/%d/%Y %H:%M:%S")
                end = datetime.strptime(end, "%m/%d/%Y %H:%M:%S")
                sighting = dict(
                    measurement="geofence.sighting",
                    time=start,
                    tags=dict(
                        place_id=place_id,
                        place_name=place_name,
                        user=v2_user,
                        platform=platform,
                        metro_id=int(metro_id) if metro_id != "#N/A" else 0,
                        metro_title=metro_title,
                        lat = float(lat) if lat != "#N/A" else 0.0,
                        lng = float(lng) if lng != "#N/A" else 0.0,
                    ),
                    fields=dict(
                        visits=int(visits),
                        visit_id=visit_id,
                        dwell_time=int(dwell_time),
                    ),
                )
                points.append(sighting)
            try:
                influx.write_points(points)
            except Exception as e:
                logging.debug(e.message)
                logging.exception(e)




manager.add_command('load_data', LoadData())

if __name__ == "__main__":
    manager.run()
