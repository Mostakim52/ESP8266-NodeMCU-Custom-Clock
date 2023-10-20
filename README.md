
# ESP8266-NodeMCU-Custom-Clock
It's a clock that I made from ESP8266 NodeMCU. It syncs the time from the web using WiFi. It even supports custom messages!

**Extra things you will need:**
-Four 7-segment displays (Cathode type)
-Four IC74273 (1 for each display)
-One IC74139 2:4 decoder(to control IC74273 clocks)
-A tactile switch
-A 10k resistor
-Two breadboards
-Lots of jumper cables


Use esp9266_clock.circ in logisim to understand what you should build.
Use the provided GIF and JPG files to understand what I built.
Just upload boot.py and networkconfig.py to ESP8266 NodeMCU the way it is.
You can modify the membday.py custom message to your liking.

**Your ESP8266 must have MicroPython firmware in it.**

