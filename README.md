### Leybold-Vacuum-Gauges

This Python code was written in order to be able to control **Leybold
ITR90** and **ITR200** vacuum gauges with a computer.
The vacuum gauges have an *RS232 interface* where they send their status
in a binary format every ~16ms.  
The gauges must be provided with the needed electric power and have to
be connected to a serial port on your computer for this software to
work. In order to achieve this, a _custom cable_ is needed, as both -
the power supply and the RS232 port - have to be connected to a single
DA-15 (or "D-sub 15") connector on each gauge.  
Once your hardware is connected you need to adjust this software to the
virtual (or physical) serial port on your computer and run it.

Currently the software (or rather the ITR classes) provide the software
/ the user with the following amenities:

* Fast updates of the measured vacuum pressure,
* a history of past pressure values,
* easy access to all status and error information the gauges provide.

Here is how this software works:

* In one thread a loop is reading data from the serial port and adds it
  to a FIFO queue.
* The ITR (90 / 200) classes start another thread where a loop reads
  from the former FIFO queue, splits the received bytes into validated,
  meaningfull messages and hands them to another method in this class
  which parses the message and adjusts the status of the class accordingly.
  A history of the vacuum pressure is stored in a thread safe ring buffer.

### Requirements

This software is written in Python v2.7, so you obviously need to install
that first. You can [obtain it][Python] for almost any operating system.
In addition you need the Python module [PySerial][] to run this software.
You can install it via `pip install pyserial` on most operating systems.

### License

Copyright (C) 2012 Philipp Klaus (Institut fuer Kernphysik Frankfurt)

> Permission is hereby granted, free of charge, to any person
> obtaining a copy of this software and associated documentation files
> (the "Software"), to deal in the Software without restriction, including
> without limitation the rights to use, copy, modify, merge, publish,
> distribute, sublicense, and/or sell copies of the Software, and to
> permit persons to whom the Software is furnished to do so, subject to
> the following conditions:
> 
> The above copyright notice and this permission notice shall be
> included in all copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
> EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
> MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
> IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
> CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
> TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
> SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[PySerial]: http://pyserial.sourceforge.net/
[Python]: http://www.python.org/getit/
