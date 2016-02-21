from flask import Blueprint, Response, render_template, url_for, request, flash, redirect, g
from flask.views import MethodView
from datetime import datetime, timedelta
from hack import config
import logging
import json

geofence = Blueprint(
    'geofences',
    __name__,
    template_folder=config.TEMPLATES,
)

class ScatterPlot(MethodView):
    def get(self):
        q = "SELECT MEAN(dwell_time) as mean FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' GROUP BY metro_title,time(1h) fill(0)"
        res = g.INFLUX.query(q)
        data = []
        for i in res.items():
            data.append({'key':i[0][1]['metro_title'], 'values':[{
                'x':p['time'],
                'y':p['mean'],
                'size':20,
                'shape':'circle',
            } for p in i[1]]})
        return render_template("geofence/scatterplot.html", data=json.dumps(data))

class StreamGraph(MethodView):
    def get(self):
        q = "SELECT MEAN(dwell_time) as mean FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' GROUP BY metro_title,time(5m) fill(0)"
        res = g.INFLUX.query(q)
        data = []
        for i in res.items():
            data.append({'key':i[0][1]['metro_title'], 'values':[{
                'x':p['time'],
                'y':p['mean'],
                'size':20,
                'shape':'circle',
            } for p in i[1]]})
        return render_template("geofence/streamgraph.html", data=json.dumps(data))

class StreamGraphCount(MethodView):
    def get(self):
        q = "SELECT COUNT(visits) as mean FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' GROUP BY metro_title,time(5m) fill(0)"
        res = g.INFLUX.query(q)
        data = []
        for i in res.items():
            data.append({'key':i[0][1]['metro_title'], 'values':[{
                'x':p['time'],
                'y':p['mean'],
                'size':20,
                'shape':'circle',
            } for p in i[1]]})
        return render_template("geofence/streamgraph.html", data=json.dumps(data))

class StreamGraphMetro(MethodView):
    def get(self, metro_id):
        logging.info(metro_id)
        q = "SELECT COUNT(visits) as mean FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' and metro_id = '{}' GROUP BY place_name,time(15m) fill(0)".format(metro_id)
        res = g.INFLUX.query(q)
        data = []
        for i in res.items():
            data.append({'key':i[0][1]['place_name'], 'values':[{
                'x':p['time'],
                'y':p['mean'],
                'size':20,
                'shape':'circle',
            } for p in i[1]]})
        return render_template("geofence/map.html", data=json.dumps(data))

class MapView(MethodView):

    def get(self):
        q = "SELECT COUNT(visits) as visits, lat, lng, place_name FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' GROUP BY metro_title"
        res = g.INFLUX.query(q)
        data = []
        for i in res.raw['series']:
            logging.info(i['values'][0][1])
            data.append({
                'count':i['values'][0][1],
                'lat':i['tags']['lat'],
                'lng':i['tags']['lng'],
            })
        return render_template("geofence/map.html", data=json.dumps(data))


geofence.add_url_rule("/scatterplot", view_func=ScatterPlot.as_view('scatterplot'))
geofence.add_url_rule("/streamgraph", view_func=StreamGraph.as_view('streamgraph'))
geofence.add_url_rule("/streamgraphcount", view_func=StreamGraphCount.as_view('streamgraphcount'))
geofence.add_url_rule("/streamgraphmetro/<metro_id>", view_func=StreamGraphMetro.as_view('streamgraphmetro'))
geofence.add_url_rule("/map", view_func=MapView.as_view('map'))
