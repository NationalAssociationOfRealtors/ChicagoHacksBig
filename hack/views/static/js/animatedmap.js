function AnimatedMap(location, data, container, tiles, heatmap_config){
    this.location = location;
    this.data = data;
    this.container = container;
    this.places = {};
    this.heatmapLayer = new HeatmapOverlay(heatmap_config);
    var tiles = new L.TileLayer(tiles, {maxZoom: 22,});
    this.map = new L.map(container, {
        layers: [tiles, this.heatmapLayer],
        center: new L.LatLng(location.coords[0], location.coords[1]),
        zoom: 12,
    });
    this.map.addControl(new Timestamp({id:"timestamp-"+this.location.id}));
    this.heatmap_data = {max:100, data:[]};
    this.init_data();
    this.heatmapLayer.setData(this.heatmap_data);
};

AnimatedMap.prototype.init_data = function(){
    for(var i in this.data){
        var s = this.data[i];
        var t = new Date(s.time);
        s.time = t.getTime();
        s.end = s.time+(s.dwell_time*1000);
        s.visible = false;
        this.places[s.place_id] = {lat:s.lat, lng:s.lng, count:0, place_id:s.place_id};
    }
};

AnimatedMap.prototype.remove_place = function(place){
    for(var i in this.heatmap_data.data){
        var p = this.heatmap_data.data[i];
        if(p.place_id == place.place_id){
            this.heatmap_data.data.slice(i, 1);
        }
    }
};

AnimatedMap.prototype.looped = function(){
    console.log("looped");
    this.heatmap_data.data = [];
};

AnimatedMap.prototype.timer = function(timestamp){
    $("#timestamp-"+this.location.id).html(timestamp);
    var now = timestamp.getTime();
    for(var i in this.data){
        var s = this.data[i];
        var place = this.places[s.place_id];
        if(s.time <= now && s.end >= now && !s.visible){
            if(!place.count) this.heatmap_data.data.push(place);
            s.visible = true;
            place.count+=10;
        }else if(s.end < now && s.visible){
            s.visible = false;
            place.count-=10;
            if(!place.count) this.remove_place(place);
        }
    }
    this.heatmapLayer.setData(this.heatmap_data);
};
