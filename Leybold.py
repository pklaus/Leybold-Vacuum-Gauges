#!/usr/bin/env python

import operator
import time
from collections import deque
import threading
from Queue import Queue, Empty

class RingBuffer(deque):
    """ http://en.wikipedia.org/wiki/Circular_buffer """
    def __init__(self, maxlen):
        deque.__init__(self, maxlen=maxlen)
    def tolist(self):
        return list(self)

class ITR(threading.Thread):
    # constants:
    msg_size_bytes = 9
    fixed_bytes = {0: chr(0x7), 1: chr(0x5) }
    checksum_byte = 8
    emission_states = { 0: 'emission off', 1: 'emission 25 uA',
                        2: 'emission 5mA', 3: 'degas' }
    pressure_units = {0: 'mbar', 1: 'Torr', 2: 'Pa'}
    # volatile constants:
    sensor_types = dict() # to be filled in __init__()
    # initial values:
    pressure = None
    version = None
    sensor_type = None
    last_update = None
    toggle_bit = None
    emission_state = None
    pressure_unit = None
    pressure_history = RingBuffer(maxlen=1000)
    type_adjusted = False

    def __init__(self, in_queue, out_queue, debug = False):
        self.debug = debug
        self.sensor_types = {
            10: ITR90,
            12: ITR200,
        }
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.closing = False # A flag to indicate thread shutdown
        threading.Thread.__init__(self)

    def run(self):
        self.read_from_queue()

    def close(self):
        self.closing = True

    def read_from_queue(self):
        """ This method serves as a buffer, validity checker
            and as a message synchroniser. """
        str_buffer = ""
        while not self.closing:
            try:
                str_buffer += self.in_queue.get(timeout=0.1)
            except Empty:
                continue
            while len(str_buffer) >= self.msg_size_bytes:
                msg = str_buffer[:9]
                if ITR.valid_message(msg):
                    self.parse_status(msg)
                    str_buffer = str_buffer[9:]
                else:
                    str_buffer = str_buffer[1:]

    @classmethod
    def check_message(cls, data):
        if len(data) < cls.msg_size_bytes:
            raise ParseError('Data has to contain 9 bytes!')
        for bytenum in cls.fixed_bytes:
            if data[bytenum] != cls.fixed_bytes[bytenum]:
                raise ParseError('Byte %d is %X, sum should be %X.' % (bytenum, ord(data[bytenum]), ord(cls.fixed_bytes[bytenum])))
        if data[cls.checksum_byte] != chr(cls.checksum256(data[1:8])):
            raise ParseError('Wrong checksum for message %s' % repr(data))

    @classmethod
    def valid_message(cls, data):
        try:
            cls.check_message(data)
            return True
        except ParseError:
            return False

    @staticmethod
    def checksum256(st):
        return reduce(operator.add, map(ord, st)) % 256

    def parse_status(self, status):
        try:
            ITR.check_message(status)
            self.parse_state(status)
            self.parse_error(status)
            self.parse_pressure(status)
            if not self.version: self.parse_version(status)
            self.parse_type(status)
            if not self.type_adjusted:
                self.fix_gauge_type()
                self.type_adjusted = True
        except ParseError:
            raise
        except Exception, e:
            if self.debug: print str(e)
            raise ParseError(e)
        self.last_update = time.time()

    def fix_gauge_type(self):
        if not isinstance(self, self.sensor_type):
            self.__class__ = self.sensor_type

    def parse_version(self, data):
        self.version = ord(data[6]) / 20.
        # This is always a number with at most 2 decimals:
        #print "%.2f" % self.version

    def parse_state(self, data):
        """ This method only implements analysing the bits being defined identically
        for the ITR90 / ITR200. It has to be overriden by derived classes to adjust
        to the specific behaviour. """
        self.parse_emission_state(data)
        self.parse_toggle_bit(data)
        self.parse_pressure_unit(data)

    def parse_emission_state(self, data):
        self.emission_state = ord(data[2]) & 0b11

    def parse_toggle_bit(self, data):
        self.toggle_bit = bool(ord(data[2]) & 0b1000)

    def parse_pressure_unit(self, data):
        self.pressure_unit = (ord(data[2]) & 0b110000) >> 4

    def parse_error(self, data):
        pass

    def parse_pressure(self, data):
        (highbyte, lowbyte) = (data[4], data[5])
        if self.pressure_unit == 0:
            self.pressure = 10.**((ord(highbyte)*256+ord(lowbyte))/4000.-12.5)
        if self.pressure_unit == 1:
            self.pressure = 10.**((ord(highbyte)*256+ord(lowbyte))/4000.-12.625)
        if self.pressure_unit == 2:
            self.pressure = 10.**((ord(highbyte)*256+ord(lowbyte))/4000.-10.5)
        self.pressure_history.append((time.time(), self.pressure))

    def parse_type(self, data):
        self.sensor_type = self.sensor_types[ord(data[7])]

    def send_message(self, payload):
        assert len(payload) == 3, "The payload to send has to contain 3 bytes."
        self.out_queue.put('\x03' + payload + str(chr(ITR.checksum256(payload))))

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

    def clear_buffers(self):
        self.clear_history()

    def __str__(self):
        return self.__class__.__name__

class ITR90(ITR):
    error_codes = {0b0000: 'no error', 0b0101: 'Pirani adjusted poorly',
            0b1000: 'BA error', 0b1001: 'Pirani error'}
    def parse_error(self, data):
        self.error_code = ord(data[3]) & 0b11110000 >> 4
    def parse_state(self, data):
        self.parse_emission_state(data)
        self.parse_adjustment_status(data)
        self.parse_toggle_bit(data)
        self.parse_pressure_unit(data)
    def parse_adjustment_status(self, data):
        """ 1000mbar adjustment """
        self.currently_adjusting = bool(ord(data[2]) & 0b100)
    def set_unit_mbar(self):
        self.send_message(chr(16)+chr(62)+chr(0))
        self.clear_buffers()
    def set_unit_Torr(self):
        self.send_message(chr(16)+chr(62)+chr(1))
        self.clear_buffers()
    def set_unit_Pa(self):
        self.send_message(chr(16)+chr(62)+chr(2))
        self.clear_buffers()
    def permanently_store_unit(self):
        self.send_message(chr(32)+chr(62)+chr(62))
    def set_degas(self, switch_on=True):
        if switch_on:
            self.send_message(chr(16)+chr(93)+chr(148))
        else:
            self.send_message(chr(16)+chr(93)+chr(105))

class ITR200(ITR):
    active_filament = {0: '1st filament', 1: '2nd filament'}
    pass

class LeyboldError(Exception):
    pass

class VacuumGaugeError(LeyboldError):
    pass

class NoDataError(VacuumGaugeError):
    pass

class ParseError(VacuumGaugeError, AssertionError):
    pass

if __name__ == "__main__":
    device = 'COM7'

    from serialman import SerialManager

    s1 = SerialManager(device)
    itr = ITR(s1.in_queue, s1.out_queue, debug = True)

    try:
        s1.start()
        itr.start()
        last_time = time.time()
        i = 0
        while True:
            time.sleep(0.3)
            if time.time()-last_time > 1.:
                i += 1
                last_time = time.time()
                try:
                    print "[%6d] Pressure (avg over last second): %.1f %s  sensor type: %s  version: %.2f" % (i, itr.get_average_pressure(), ITR.pressure_units[itr.pressure_unit], itr, itr.version)
                    print "Samples in buffer: %d" % len(itr.pressure_history)
                except NoDataError:
                    print "No Data"
                itr.clear_history()
                print "Toggle Bit:", itr.toggle_bit
                print "Emission State:", ITR.emission_states[itr.emission_state]
                print "Pressure Unit:", ITR.pressure_units[itr.pressure_unit]
                if type(itr) == ITR90:
                    print "Error Code:", ITR90.error_codes[itr.error_code]
                #if i == 5: itr.permanently_store_unit()
                if i % 4 == 1:
                    itr.set_unit_Torr()
                if i % 4 == 3:
                    itr.set_unit_mbar()
                print ""
    except KeyboardInterrupt:
        s1.close()
        itr.close()
    finally:
        s1.close()
        itr.close()
    s1.join()
    itr.join()
