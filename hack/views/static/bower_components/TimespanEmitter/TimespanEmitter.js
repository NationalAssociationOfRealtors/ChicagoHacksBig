;(function () {
    'use strict';

    function TimespanEmitter(start_time, end_time, interval, playback_rate, loop){
        this.start_time = typeof start_time !== 'number' ? start_time.getTime() : start_time;
        this.end_time = typeof end_time !== 'number' ? end_time.getTime() : end_time;
        this.interval = interval;
        this.loop = loop || false;
        this.playback_rate = playback_rate;
        this.total_time = this.end_time-this.start_time;//18000000
        this.num_steps = Math.ceil(this.total_time/this.interval);//18000
        this.event_rate = (this.total_time/this.playback_rate)/this.num_steps;//1800000/18000
        this.step_increment = this.total_time/this.num_steps;
        this.last = performance.now()-this.event_rate;
        this.counter = 0;
    };

    var proto = TimespanEmitter.prototype;
    var exports = this;

    proto.addListener = function(evt, callback, scope){
        var events = this._getEvents();
        var listeners = events[evt] || (events[evt]=[]);
        listeners.push({callback:callback, scope:scope});
        return this;
    };

    proto.start = function(){
        this.run();
    };

    proto.run = function(timestamp){
        requestAnimationFrame(this.run.bind(this));
        var diff = (timestamp-this.last);
        if(diff >= this.event_rate && this.counter < this.num_steps){
            var add = this.start_time+(this.counter*this.step_increment);
            var current = new Date(add);
            for(var i in this._getEvents()['timer']){
                var cb = this._getEvents()['timer'][i];
                cb.callback.apply(cb.scope, [current]);
            }
            this.counter++;
            this.last = timestamp;
        }else if(this.counter >= this.num_steps && this.loop){
            this.counter = 0;
            for(var i in this._getEvents()['looped']){
                var cb = this._getEvents()['looped'][i];
                cb.callback.apply(cb.scope, []);
            }
        }
    };

    proto._getEvents = function(){
        return this._events || (this._events = {});
    };

    // Expose the class either via AMD, CommonJS or the global object
    if (typeof define === 'function' && define.amd) {
        define(function () {
            return TimespanEmitter;
        });
    }
    else if (typeof module === 'object' && module.exports){
        module.exports = TimespanEmitter;
    }
    else {
        exports.TimespanEmitter = TimespanEmitter;
    }
}.call(this));
