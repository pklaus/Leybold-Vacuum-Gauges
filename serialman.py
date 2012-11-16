#!/usr/bin/env python

import serial
import threading
import time
from Queue import Queue, Empty

class SerialManager(threading.Thread):
    """ This class has been written by
        Philipp Klaus and can be found on
        https://gist.github.com/4039175 .  """
    def __init__(self, device, kwargs=dict()):
        settings = dict()
        settings['baudrate'] = 9600
        settings['bytesize'] = serial.EIGHTBITS
        settings['parity'] = serial.PARITY_NONE
        settings['stopbits'] = serial.STOPBITS_ONE
        settings['timeout'] = 0
        settings.update(kwargs)
        self._kwargs = settings
        self.ser = serial.Serial(device, **self._kwargs)
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.closing = False # A flag to indicate thread shutdown
        self.sleeptime = 0.0005
        threading.Thread.__init__(self)

    def run(self):
        while not self.closing:
            time.sleep(self.sleeptime)
            in_data = self.ser.read(9)
            if in_data: self.in_queue.put(in_data)
            try:
                out_buffer = self.out_queue.get_nowait()
                self.ser.write(out_buffer)
            except Empty:
                pass
        self.ser.close()

    def close(self):
        self.closing = True

if __name__ == "__main__":
    device = '/dev/tty.usbserial'

    s1 = SerialManager(device)
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
