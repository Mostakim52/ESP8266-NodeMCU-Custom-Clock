# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()

import network
AP_SSID = "ESP8266"
AP_PASSWORD = "11223344"
# Disable the automatic AP creation at boot
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD)

import membday