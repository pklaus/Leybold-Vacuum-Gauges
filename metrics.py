#!/usr/bin/env python2.7

from collections import deque

class RingBuffer(deque):
    """ http://en.wikipedia.org/wiki/Circular_buffer """
    def __init__(self, maxlen):
        deque.__init__(self, maxlen=maxlen)
    def to_list(self):
        return list(self)

import threading
import time

class DataCollector(object):
    def __init__(self, callback, update_every_seconds, maxlen=1000):
        self.__running = threading.Event()
        self.callback  = callback
        self.update_every_seconds = update_every_seconds
        self.rbuffer = RingBuffer(maxlen)
    def start(self):
        self.__running.set()
        self.schedule()
    def schedule(self):
        self.__timer = threading.Timer(self.update_every_seconds, self.run)
        self.__timer.start()
    def run(self):
        if self.__running.is_set(): self.schedule()
        self.rbuffer.append( (time.time(), self.callback()) )
    def stop(self):
        try:
            self.__running.clear()
            self.__timer.cancel()
        except:
            pass

import math
def get_metric(dc, seconds, transformation):
    history = dc.rbuffer.to_list()
    num_entries = min(len(history), int(math.floor(float(seconds) / dc.update_every_seconds)))
    history = history[-num_entries:]
    val = .0
    tim = .0
    for entry in history:
        tim += entry[0]
        val += transformation(entry[1])
    return (tim/len(history), val/len(history))

def returner(argument):
    return argument

if __name__ == "__main__":
    import random
    dc_10ms = DataCollector(random.random, .0001, maxlen=20)
    def get_10ms_metric():
        return get_metric(dc_10ms, 0.1, returner)[1]
    dc_100ms = DataCollector(get_10ms_metric, 0.1, maxlen=100)
    try:
        dc_10ms.start()
        dc_100ms.start()
        for i in range(0,10):
            time.sleep(1.)
            (tim, val) = get_metric(dc_100ms, 1, returner)
            print "average time: %f" % tim
            print "average value: %f" % val
    finally:
        dc_100ms.stop()
        dc_10ms.stop()
    time.sleep(0.01)
