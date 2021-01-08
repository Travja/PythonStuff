import os
import time
import pychromecast
import sys
import random
import volume

chromecasts, browser = pychromecast.get_chromecasts()
name = 'Jeeves'
#print(chromecasts)
for cc in chromecasts:
    if cc.device.friendly_name == name:
        cast = cc
        volume.init(cast)
        print("Found " + name)
        break
    else:
        print("Could not find '" + name + "'")
        sys.exit(1)

# Wait for cast device to be ready
cast.wait()

volume.read("It's time for bed, sir.")

# Shut down discovery
pychromecast.discovery.stop_discovery(browser)
sys.exit(0)
