#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
from bottle import Bottle, static_file, TEMPLATE_PATH
from bottle import jinja2_view as view
from apiserver import api, LeyboldGaugesBottlePlugin

interface = Bottle()

STATIC_ROOT = os.path.join(os.path.split(os.path.realpath(__file__))[0],'./webresources/static/')
TEMPLATE_PATH.append(os.path.join(os.path.split(os.path.realpath(__file__))[0],'./webresources/views/'))

@interface.route('/')
@view('home.jinja2')
def index_page():
    return dict()

@interface.route('/digital-display')
@view('digital-display.jinja2')
def entire_history():
    return dict()

@interface.route('/static/<path:path>')
def static(path):
    return static_file(path, root=STATIC_ROOT)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the Leybold Vacuum Gauges Interface Web-Server')
    parser.add_argument('-p', '--port', default='8090', help='The port to run the web server on.')
    parser.add_argument('-6', '--ipv6', action='store_true', help='Listen to incoming connections via IPv6 instead of IPv4.')
    parser.add_argument('-d', '--debug', action='store_true', help='Start in debug mode (with verbose HTTP error pages.')
    parser.add_argument('serial_ports', metavar='SERIAL_PORT', nargs='+',
                        help='The serial port to connect to, sth. like COM7 on Windows /dev/ttyUSB1 on Linux.')
    args = parser.parse_args()

    if args.debug and args.ipv6:
        args.error('You cannot use IPv6 in debug mode, sorry.')

    leybold_gauges_plugin = LeyboldGaugesBottlePlugin(args.serial_ports)
    api.install(leybold_gauges_plugin)
    interface.mount('/api', api)

    if args.debug:
        interface.run(host='0.0.0.0', port=args.port, debug=True, reloader=True)
    else:
        if args.ipv6:
            # CherryPy is Python3 ready and has IPv6 support:
            interface.run(host='::', server='cherrypy', port=args.port)
        else:
            interface.run(host='0.0.0.0', server='cherrypy', port=args.port)
