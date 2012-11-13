### Leybold-Vacuum-Gauges

This Python code was written in order to be able to control Leybold
ITR90 and ITR200 vacuum gauges with a computer.
Basically they come with a DSUB-15 connector which combines its power
supply with a normal RS232 Port. Just connect that to a serial port of
your computer and start reading the values from the gauges.

### Requirements

You need [PySerial][] to run this software. You can install it via
`pip install pyserial` on most operating systems.

### License

Copyright (C) 2012 Philipp Klaus, IKF

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[PySerial]: http://pyserial.sourceforge.net/
