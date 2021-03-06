#!/usr/bin/env python

import threading
import time
from Queue import Queue
from sampledata import sample_itr90
from Leybold import ITR, NoDataError

class DummyDataProvider(threading.Thread):
    def __init__(self, dummy_data):
        self.in_queue = Queue()
        self.closing = False # A flag to indicate thread shutdown
        self.sleeptime = 0.001
        self.dummy_data = dummy_data
        threading.Thread.__init__(self)

    def run(self):
        j = 0
        while not self.closing:
            time.sleep(self.sleeptime)
            self.in_queue.put(self.dummy_data[j])
            j += 1
            j %= len(self.dummy_data)

    def close(self):
        self.closing = True


if __name__ == "__main__":

    d1 = DummyDataProvider(sample_itr90)
    itr = ITR(d1.in_queue, Queue(), debug = True)

    try:
        d1.start()
        itr.start()
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
                    print "[%6d] Pressure (avg over last second): %.1f mbar  sensor type: %s  version: %f" % (i, itr.get_average_pressure(), itr, itr.version)
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
