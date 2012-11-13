#!/usr/bin/env python

import threading
import time
from Queue import Queue
from sampledata import sample_itr90
from Leybold import ITR

class DummyDataProvider(threading.Thread):
    def __init__(self, dummy_data):
        self.in_queue = Queue()
        self.closing = False # A flag to indicate thread shutdown
        self.sleeptime = 0.003
        self.dummy_data = dummy_data
        threading.Thread.__init__(self)

    def run(self):
        j = 0
        while not self.closing:
            time.sleep(self.sleeptime)
            self.in_queue.put(self.dummy_data[j])
            j += 1
            j = j % len(self.dummy_data)

    def close(self):
        self.closing = True


if __name__ == "__main__":

    d1 = DummyDataProvider(sample_itr90)
    d1.start()
    itr = ITR(d1.in_queue, Queue(), debug = True)
    itr.start()

    try:
        last_time = time.time()
        i = 0
        update_time = 1.
        while True:
            # we need to sleep in the main thread to allow for the other threads to run
            time.sleep(update_time/20.)
            if (time.time()-last_time) > update_time:
                i += 1
                last_time = time.time()
                try:
                    itr.fix_gauge_type()
                    print "[%8d] Average pressure: %.1f mbar  sensor type: %s  software version: %f" % (i, itr.get_average_pressure(), itr.sensor_type, itr.version)
                except NoDataError:
                    pass
                itr.clear_history()
    except KeyboardInterrupt:
        d1.close()
        itr.close()
    finally:
        d1.close()
        itr.close()
    d1.join()
    itr.join()
