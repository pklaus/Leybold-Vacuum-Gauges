### ToDo

* Implementation of the back channel:  
  Sending binary messages back to the vacuum gauges.
* Including a unittest that uses the sample data.
  (Inspiration to be found [here](http://goo.gl/XbrJ9)?)
* Automatically test for the gauge type
  (and thus change the instance class) when:
  * parsing the received status for the first time?
  * every n received data bits?
