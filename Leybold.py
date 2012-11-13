#!/usr/bin/env python

from serialrecv import SerialReceiver
import operator
import time
from collections import deque

class ItrUpdater(object):
    fixed_bytes = {0: chr(0x7), 1: chr(0x5) }
    checksum_byte = 8
    byte_num = 9
    def __init__(self, callback, debug=False):
        self.buf = ""
        self.in_sync = False
        self.callback = callback
        self.debug = debug
        self.last_time = time.time()

    def add_new_input(self, data):
        self.buf += data
        if not self.enough_bytes():
            return
        if not self.in_sync:
            if self.synchronize():
                #print 'syncing'
                self.in_sync = True
            else:
                return
        if not self.enough_bytes():
            return
        message = self.get_message()
        if message != False:
            self.callback(message)
            #print time.time() - self.last_time
            self.last_time = time.time()
        else:
            self.buf = self.buf[1:]
            self.in_sync = False

    def enough_bytes(self):
        return len(self.buf) >= self.byte_num

    def get_message(self):
        for bytenum in self.fixed_bytes:
            if self.buf[bytenum] != self.fixed_bytes[bytenum]:
                return False
        if self.buf[self.checksum_byte] != chr(self.checksum256(self.buf[1:8])):
            if self.debug: print 'problematic message %s' % repr(self.buf[:9])
            return False
        buf = self.buf[0:9]
        self.buf = self.buf[9:]
        return buf

    def checksum256(self, st):
        return reduce(operator.add, map(ord, st)) % 256

    def synchronize(self):
        pos = self.buf.find(self.fixed_bytes[0])
        if pos >= 0:
            self.buf = self.buf[pos:]
            return True
        return False

class RingBuffer(deque):
    def __init__(self, maxlen):
        deque.__init__(self, maxlen=maxlen)
    # http://en.wikipedia.org/wiki/Circular_buffer
    def tolist(self):
        return list(self)

class ITR(object):
    # constants:
    sensor_types = dict() # to be filled in __init__()
    # initial values:
    pressure = None
    version = None
    sensor_type = None
    last_update = None
    pressure_history = RingBuffer(maxlen=1000)
    def __init__(self, debug = False):
        self.debug = debug
        self.sensor_types = {
            10: ITR90,
            12: ITR200,
        }
    def parse_status(self, status):
        #self.check_message(status)
        try:
            #self.parse_state(status)
            #self.parse_error(status)
            self.parse_pressure(status)
            self.parse_version(status)
            self.parse_type(status)
        except ParseError:
            raise
        except Exception, e:
            if self.debug: print str(e)
            raise ParseError(e)
        self.last_update = time.time()
        #print "%.3E" % self.pressure

    def parse_version(self, data):
        self.version = ord(data[6]) / 20.

    def parse_state(self, data):
        return NotImplemented

    def parse_error(self, data):
        return NotImplemented

    def parse_pressure(self, data):
        (highbyte, lowbyte) = (data[4], data[5])
        self.pressure = 10.**((ord(highbyte)*256+ord(lowbyte))/4000.-12.5)
        self.pressure_history.append((time.time(), self.pressure))

    def parse_type(self, data):
        self.sensor_type = self.sensor_types[ord(data[7])]

    def get_average_pressure(self, num_samples=60):
        # 1 sample / 0.016 seconds = 62.5 samples per second
        if self.debug and num_samples > len(self.pressure_history):
            print "The buffer contains only %i samples. Cannot calculate the average over %i values." % (len(self.pressure_history), num_samples)
        if len(self.pressure_history) == 0:
            raise NoDataError('cannot calculate an average pressure without any values.')
        num_samples = min(num_samples, len(self.pressure_history))
        return sum([hist[1] for hist in self.pressure_history.tolist()[-num_samples:]])/float(num_samples)

    def clear_history(self):
        self.pressure_history.clear()

class ITR90(ITR):
    pass

class ITR200(ITR):
    pass

class LeyboldError(Exception):
    pass

class VacuumGaugeError(LeyboldError):
    pass

class NoDataError(VacuumGaugeError):
    pass

class ParseError(VacuumGaugeError):
    pass

toHex = lambda x:"".join([hex(ord(c))[2:].zfill(2) for c in x])
def printer(data):
    print [toHex(byte) for byte in data]


if __name__ == "__main__":
    device = '/dev/tty.usbserial-FTUN6PL6A'

    s1 = SerialReceiver(device)
    s1.start()

    itr90 = ITR90(debug = True)

    #iu = ItrUpdater(printer)
    iu = ItrUpdater(itr90.parse_status, debug=True)

    try:
        last_time = time.time()
        i = 0
        while True:
            time.sleep(0.001)
            iu.add_new_input(s1.pop_buffer())
            if time.time()-last_time > 1.:
                i += 1
                last_time = time.time()
                try:
                    print "[%8d] Average pressure: %.1f mbar" % (i, itr90.get_average_pressure())
                except NoDataError:
                    pass
                itr90.clear_history()
    except KeyboardInterrupt:
        s1.close()
    finally:
        s1.close()
    s1.join()
