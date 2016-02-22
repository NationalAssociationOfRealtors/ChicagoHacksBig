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

locations = [
    {'id':3, 'name':'Chicago, IL', 'coords':[41.879676, -87.632599]},
    {'id':22, 'name':'Madison, WI', 'coords':[43.073186, -89.405736]},
    {'id':29, 'name':'Toronto, ON, CA', 'coords':[43.653606, -79.381498]},
    {'id':25, 'name':'Boston, MA', 'coords':[42.359287, -71.056815]},
    {'id':10, 'name':'New York, NY', 'coords':[40.712852, -73.997237]},
    {'id':42, 'name':'Indianapolis, IN', 'coords':[39.767562, -86.168463]},
    {'id':36, 'name':'St. Louis, MO', 'coords':[38.627942, -90.200757]},
    {'id':47, 'name':'Louisville, KY', 'coords':[38.255073, -85.759862]},
    {'id':24, 'name':'Nashville, TN', 'coords':[36.161062, -86.782506]},
    {'id':1, 'name':'Austin, TX', 'coords':[30.267961, -97.745856]},
    {'id':11, 'name':'Dallas, TX', 'coords':[32.778453, -96.793145]},
    {'id':2, 'name':'San Antonio, TX', 'coords':[30.267961, -97.750663]},
    {'id':30, 'name':'Los Angeles, CA', 'coords':[34.057735, -118.257954]},
    {'id':18, 'name':'Bay Area', 'coords':[37.774997, -122.418031]},
    {'id':19, 'name':'Portland, OR', 'coords':[45.522213, -122.680516]},
    {'id':9, 'name':'Seattle, WA', 'coords':[47.606893, -122.333166]},
    {'id':32, 'name':'Vancouver, BC, CA', 'coords':[49.281868, -123.122885]},
    {'id':50, 'name':'Victoria, BC, CA', 'coords':[48.428130, -123.363824]},
]

def get_location(id):
    for l in locations:
        if l['id'] == id: return l

class Index(MethodView):

    def get(self):
        return render_template("index.html", locations=locations)

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
        location = get_location(int(metro_id))
        q = "SELECT COUNT(visits) as mean FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' and metro_id = '{}' GROUP BY place_name,time(15m) fill(none)".format(metro_id)
        res = g.INFLUX.query(q)
        data = []
        for i in res.items():
            data.append({'key':i[0][1]['place_name'], 'values':[{
                'x':p['time'],
                'y':p['mean'],
                'size':20,
                'shape':'circle',
            } for p in i[1]]})
        return render_template("geofence/streamgraph.html", data=json.dumps(data), name=location['name'])

class MapView(MethodView):

    def get(self):
        q = "SELECT COUNT(visits) as visits FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' GROUP BY metro_title,lat, lng, place_name"
        res = g.INFLUX.query(q)
        data = []
        for i in res.raw['series']:
            data.append({
                'count':i['values'][0][1],
                'lat':i['tags']['lat'],
                'lng':i['tags']['lng'],
            })
        return render_template("geofence/map.html", data=json.dumps(data))

class MapHeatmapAnimatedView(MethodView):

    def get(self):
        q = "SELECT COUNT(visits) as visits FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' GROUP BY metro_title,lat,lng,time(15m)"
        res = g.INFLUX.query(q)
        data = []
        for i in res.raw['series']:
            data.append({
                'values':i['values'],
                'lat':i['tags']['lat'],
                'lng':i['tags']['lng'],
            })
        return render_template("geofence/mapanimated.html", data=json.dumps(data), locations=json.dumps(locations))

class MapHeatmapMetroView(MethodView):

    def get(self, metro_id):
        q = "SELECT COUNT(visits) as visits FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' GROUP BY metro_title,lat,lng,time(15m)"
        res = g.INFLUX.query(q)
        data = []
        for i in res.raw['series']:
            data.append({
                'values':i['values'],
                'lat':i['tags']['lat'],
                'lng':i['tags']['lng'],
            })
        return render_template("geofence/mapmetro.html", data=json.dumps(data), metro_id=metro_id, locations=json.dumps(locations))

class MapSightingsMetroView(MethodView):

    def get(self, metro_id):
        q = "SELECT lat, lng, dwell_time, place_id FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' and metro_id='{}'".format(metro_id)
        logging.info(q)
        res = g.INFLUX.query(q)
        data = []
        for i in res.get_points():
            logging.info(i)
            data.append({
                'dwell_time':i['dwell_time'],
                'lat':i['lat'],
                'lng':i['lng'],
                'time':i['time'],
                'place_id':i['place_id']
            })
        return render_template("geofence/mapmetrosightings.html", data=json.dumps(data), metro_id=metro_id, locations=json.dumps(locations))

class MapSightingsMultipleMetroView(MethodView):

    def get(self, metro_ids):
        ids = metro_ids.split(",")
        metros = {}
        for id in ids:
            q = "SELECT lat, lng, dwell_time, place_id FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' and metro_id='{}'".format(id)
            res = g.INFLUX.query(q)
            metros['metro_{}'.format(id)] = {'id':id, 'data':[]}
            for i in res.get_points():
                metros['metro_{}'.format(id)]['data'].append({
                    'dwell_time':i['dwell_time'],
                    'lat':i['lat'],
                    'lng':i['lng'],
                    'time':i['time'],
                    'place_id':i['place_id']
                })
        return render_template("geofence/multiplemaps.html", data=json.dumps(metros), locations=json.dumps(locations))


class Circles(MethodView):

    def get(self):
        q = "SELECT COUNT(visits) as visits, MEAN(dwell_time) as dwell_time FROM \"geofence.sighting\" WHERE time > '2016-02-18T22:00:00Z' and time < '2016-02-19T12:00:00Z' GROUP BY metro_title,place_name,time(15m) fill(0)"
        res = g.INFLUX.query(q)
        data = {}
        for i in res.items():
            metro = data.setdefault("metro_{}".format(i[0][1]['metro_title']), {})
            place = metro.setdefault(i[0][1]['place_name'], [])
            for p in i[1]:
                place.append(p)

        return render_template('3d.html', data=json.dumps(data))

geofence.add_url_rule("/", view_func=Index.as_view('index'))
geofence.add_url_rule("/scatterplot", view_func=ScatterPlot.as_view('scatterplot'))
geofence.add_url_rule("/streamgraph", view_func=StreamGraph.as_view('streamgraph'))
geofence.add_url_rule("/streamgraphcount", view_func=StreamGraphCount.as_view('streamgraphcount'))
geofence.add_url_rule("/streamgraphmetro/<metro_id>", view_func=StreamGraphMetro.as_view('streamgraphmetro'))
geofence.add_url_rule("/map", view_func=MapView.as_view('map'))
geofence.add_url_rule("/map/<metro_id>/sightings", view_func=MapSightingsMetroView.as_view('mapmetrosightings'))
geofence.add_url_rule("/map/multiple/<metro_ids>/sightings", view_func=MapSightingsMultipleMetroView.as_view('mapmulitplemetrosightings'))
geofence.add_url_rule("/map/<metro_id>", view_func=MapHeatmapMetroView.as_view('mapmetro'))
geofence.add_url_rule("/mapanimated", view_func=MapHeatmapAnimatedView.as_view('mapanimated'))
geofence.add_url_rule("/circles", view_func=Circles.as_view('circles'))
