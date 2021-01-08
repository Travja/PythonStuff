"""
Example on how to use the Spotify Controller.
NOTE: You need to install the spotipy and spotify-token dependencies.

This can be done by running the following:
pip install spotify-token
pip install git+https://github.com/plamere/spotipy.git
"""
import argparse
import logging
import time
import sys
import random
import asyncio

import pychromecast
from pychromecast.controllers.spotify import SpotifyController
import spotify_token as st
import spotipy
import zeroconf

CAST_NAME = "Jeeves"

parser = argparse.ArgumentParser(
    description="Example on how to use the Spotify Controller."
)
parser.add_argument("--show-debug", help="Enable debug log", action="store_true")
parser.add_argument(
    "--show-zeroconf-debug", help="Enable zeroconf debug log", action="store_true"
)
parser.add_argument(
    "--cast", help='Name of cast device (default: "%(default)s")', default=CAST_NAME
)
#parser.add_argument("--user", help="Spotify username", required=True)
#parser.add_argument("--password", help="Spotify password", required=True)
parser.add_argument(
    "--uri",
    help='Spotify uri(s) (default: "%(default)s")',
    default=["unset"],
    nargs="+",
)
args = parser.parse_args()

if args.show_debug:
    logging.basicConfig(level=logging.DEBUG)
    # Uncomment to enable http.client debug log
    # http_client.HTTPConnection.debuglevel = 1
if args.show_zeroconf_debug:
    print("Zeroconf version: " + zeroconf.__version__)
    logging.getLogger("zeroconf").setLevel(logging.DEBUG)

chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[args.cast])
print("Discovered: {}".format([o.device.friendly_name for o in chromecasts]))
cast = list(chromecasts)[0]

if not cast:
    print('No chromecast with name "{}" discovered'.format(args.cast))
    print("Discovered casts: {}".format(chromecasts))
    sys.exit(1)

print("Casting to: {}".format(cast.device.friendly_name))
print()


# Wait for connection to the chromecast
cast.wait()

spotify_device_id = None

# Create a spotify token
data = st.start_session('AQCNDwe7-v4N1F0SLn_HbosHFppfrYvUW-RON3cq-l17dFWIxNEItMSC_Ydm3kN1sBnz8lIucTzx9XC0B-fYAdTi_tODOmqf0mR2LNVJ9Q', '03439c8c-2dc1-45c4-85e1-55726b431177')
access_token = data[0]
expires = data[1] - int(time.time())

# Create a spotify client
client = spotipy.Spotify(auth=access_token)
if args.show_debug:
    spotipy.trace = True
    spotipy.trace_out = True

# Launch the spotify app on the cast we want to cast to
sp = SpotifyController(access_token, expires)
cast.register_handler(sp)
sp.launch_app()

if not sp.is_launched and not sp.credential_error:
    print("Failed to launch spotify controller due to timeout")
    sys.exit(1)
if not sp.is_launched and sp.credential_error:
    print("Failed to launch spotify controller due to credential error")
    sys.exit(1)

# Query spotify for active devices
devices_available = client.devices()

# Match active spotify devices with the spotify controller's device id
for device in devices_available["devices"]:
    if device["id"] == sp.device:
        spotify_device_id = device["id"]
        break

if not spotify_device_id:
    print('No device with id "{}" known by Spotify'.format(sp.device))
    print("Known devices: {}".format(devices_available["devices"]))
    sys.exit(1)

def getName(str):
    ttype = str.split(":")[1]
    item = client.track(str) if ttype == 'track' \
        else client.album(str) if ttype == 'album' \
        else client.artist(str) if ttype == 'artist' \
        else client.playlist(str)
    return item['name']

terminate = False
async def setFreakingVolume(level):
    global terminate
    terminate = False
    i = 150
    last = 0.001
    while i > 0 and not terminate:
        i -= 1
        cast.wait()
        diff = 0 if last == 0.001 else 0.001
        last = diff
        cast.set_volume(level - diff)
        await asyncio.sleep(0.05)
    cast.set_volume(level)
    if terminate:
        print("Terminated task.")
    terminate = False
    
# Start playback
async def playMusic():
    #client.next_track(device_id=spotify_device_id)
    if args.uri[0] == 'unset':
        dat = client.user_playlists("12144944831")['items'];
        dd = [o['id'] for o in dat]
        dd2 = [o['name'] for o in dat]
        choice = random.choice(dd)
        uuri = "spotify:playlist:{}".format(choice)
        print("♫ Playing " + dd2[dd.index(choice)] + " ♫")
        client.start_playback(device_id=spotify_device_id, context_uri=uuri)
        client.shuffle(True, device_id=spotify_device_id)
    else:
        name = getName(args.uri[0])
        if args.uri[0].find("track") > 0:
            client.start_playback(device_id=spotify_device_id, uris=args.uri)
        else:
            client.start_playback(device_id=spotify_device_id, context_uri=args.uri[0])
            client.shuffle(True, device_id=spotify_device_id)
        print("♫ Playing: " + name + " ♫")
    # Shut down discovery
    pychromecast.discovery.stop_discovery(browser)

async def go():
    m = playMusic()
    vol = setFreakingVolume(0.3)
    await m
    await vol

asyncio.run(go())
sys.exit(0)
