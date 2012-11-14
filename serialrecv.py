#!/usr/bin/env python

import serial
import threading
import time
from Queue import Queue

class SerialReceiver(threading.Thread):
    """ This class has been written by
        Philipp Klaus and can be found on
        https://gist.github.com/4039175 .  """
    def __init__(self, device, *args):
        self._target = self.read
        self._args = args
        self.ser = serial.Serial(device, timeout = 0)
        self.in_queue = Queue()
        self.closing = False # A flag to indicate thread shutdown
        self.sleeptime = 0.0005
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)

    def read(self):
        while not self.closing:
            time.sleep(self.sleeptime)
            data = self.ser.read(6)
            if data: self.in_queue.put(data)
        self.ser.close()

    def write(data):
        self.ser.write(data)

    def close(self):
        self.closing = True


if __name__ == "__main__":
    device = '/dev/tty.usbserial'

    s1 = SerialReceiver(device)
    s1.start()

    try:
        while True:
            data = s1.in_queue.get()
            print repr(data)
    except KeyboardInterrupt:
        s1.close()
    finally:
        s1.close()
    s1.join()
