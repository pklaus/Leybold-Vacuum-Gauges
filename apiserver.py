#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import inspect
from serialman import SerialManager
from serial.serialutil import SerialException
from Leybold import ITR, LeyboldError

from bottle import Bottle, HTTPError, PluginError, response, request, abort

class LeyboldGaugesBottlePlugin(object):
    ''' This plugin provides Bottle routes which accept a `gauges` argument
    with an interface to Leybold Gauges.
    It is based on the example found at
    http://bottlepy.org/docs/stable/plugindev.html#plugin-example-sqliteplugin
    '''
    name = 'gauges'
    api = 2

    def __init__(self, device_names, keyword='gauges'):
        self.devices = dict()
        for device_name in device_names:
            self.devices[device_name] = dict()
            try:
                self.devices[device_name]['SerialManager'] = SerialManager(device_name)
                in_queue = self.devices[device_name]['SerialManager'].in_queue
                out_queue = self.devices[device_name]['SerialManager'].out_queue
                self.devices[device_name]['ITR'] = ITR(in_queue, out_queue, debug = True)
                self.devices[device_name]['nickname'] = ''
            except SerialException:
                sys.stdout.write('Could not open serial device {0}\n'.format(device_name))
                sys.exit(1)
        self.keyword = keyword

    def setup(self, app):
        for other in app.plugins:
            if not isinstance(other, LeyboldGaugesBottlePlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another MaxiGauge plugin with conflicting settings (non-unique keyword).")
        for device in self.devices:
            try:
                self.devices[device]['SerialManager'].start()
                self.devices[device]['ITR'].start()
            except Exception, e:
                raise PluginError("Could not connect to Leybold Gauge with device name %s. Error: %s" % (device, e) )

    def apply(self, callback, context):
        keyword = self.keyword
        # Test if the original callback accepts a 'maxigauge' keyword.
        # Ignore it if it does not need a handle.
        args = inspect.getargspec(context.callback)[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            gauges = self.devices
            kwargs[keyword] = gauges
            try:
                rv = callback(*args, **kwargs)
            except LeyboldError, e:
                raise HTTPError(503, "Leybold unavailable: " + str(e) )
            finally:
                pass
            return rv

        return wrapper

    def close(self):
        for device in self.devices:
            self.devices[device]['SerialManager'].close()
            self.devices[device]['ITR'].close()
        for device in self.devices:
            self.devices[device]['SerialManager'].join()
            self.devices[device]['ITR'].join()

api = Bottle()

@api.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    https://gist.github.com/richard-flosi/3789163
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@api.route('/gauges')
def list_gauges(gauges):
    retval = []
    for device in gauges:
        retval.append(dict(port=device, nickname=gauges[device]['nickname']))
    return dict(gauges=retval)

@api.route('/pressure')
@api.route('/pressure/')
def all_pressures(gauges):
    return pressure('all', gauges)

@api.route('/pressure/<which>')
def pressure(which, gauges):
    status = dict()
    if which == 'all':
        devices = list(gauges)
    elif which in gauges:
        devices = [which]
    else:
        abort(504, 'This gauge does not exist')
    for device in devices:
        itr = gauges[device]['ITR']
        status[device] = dict(pressure=itr.get_average_pressure(num_samples = 30))
        #itr.clear_history()
    return status

@api.get('/nickname/<which>')
def pressure(which, gauges):
    status = dict()
    if which == 'all':
        devices = list(gauges)
    elif which in gauges:
        devices = [which]
    else:
        abort(504, 'This gauge does not exist')
    for device in devices:
        status[device] = dict(nickname=gauges[device]['nickname'])
    return status

@api.post('/nickname/<which>')
def pressure(which, gauges):
    nickname = request.forms.get('nickname')
    status = dict()
    if which not in gauges:
        abort(504, 'This gauge does not exist')
    gauges[which]['nickname'] = nickname
    status = dict(which=dict(nickname=gauges[which]['nickname']))
    return status

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the Leybold Vacuum Gauges API Web-Server')
    parser.add_argument('-p', '--port', default='8080', help='The port to run the web server on.')
    parser.add_argument('-6', '--ipv6', action='store_true', help='Listen to incoming connections via IPv6 instead of IPv4.')
    parser.add_argument('-d', '--debug', action='store_true', help='Start in debug mode (with verbose HTTP error pages.')
    parser.add_argument('serial_ports', metavar='SERIAL_PORT', nargs='+',
                        help='The serial port to connect to, sth. like COM7 on Windows /dev/ttyUSB1 on Linux.')
    args = parser.parse_args()

    if args.debug and args.ipv6:
        args.error('You cannot use IPv6 in debug mode, sorry.')

    leybold_gauges_plugin = LeyboldGaugesBottlePlugin(args.serial_ports)
    api.install(leybold_gauges_plugin)

    if args.debug:
        api.run(host='0.0.0.0', port=args.port, debug=True, reloader=True)
    else:
        if args.ipv6:
            # CherryPy is Python3 ready and has IPv6 support:
            api.run(host='::', server='cherrypy', port=args.port)
        else:
            api.run(host='0.0.0.0', server='cherrypy', port=args.port)
