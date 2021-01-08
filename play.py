import argparse
import logging
import random
import time
import pychromecast
import sys

import pychromecast
from pychromecast.controllers.spotify import SpotifyController
import spotify_token as st
import spotipy
import zeroconf

import volume

CAST_NAME = "Jeeves"

parser = argparse.ArgumentParser(
    description="Media controller to say a message and play Spotify"
)
parser.add_argument(
    "--msg", help="The message to say", default="Hey, it's time for bed."
)
parser.add_argument(
    "--cast", help='Name of cast device (default: "%(default)s")', default=CAST_NAME
)
parser.add_argument(
    "--uri",
    help='Spotify uri(s) (default: "%(default)s")',
    default=["unset"],
    nargs="+",
)
args = parser.parse_args()
    

chromecasts, browser = pychromecast.get_chromecasts()
for cc in chromecasts:
    if cc.device.friendly_name == CAST_NAME:
        cast = cc
        volume.init(cast)
        print("Found " + CAST_NAME)
        break
    else:
        print("Could not find '" + CAST_NAME + "'")
        sys.exit(1)

def play(args):
    cast.wait()
    spotify_device_id = None

    # Create a spotify token
    data = st.start_session('AQCNDwe7-v4N1F0SLn_HbosHFppfrYvUW-RON3cq-l17dFWIxNEItMSC_Ydm3kN1sBnz8lIucTzx9XC0B-fYAdTi_tODOmqf0mR2LNVJ9Q', '03439c8c-2dc1-45c4-85e1-55726b431177')
    access_token = data[0]
    expires = data[1] - int(time.time())

    # Create a spotify client
    client = spotipy.Spotify(auth=access_token)

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
        
    def getTracks(uri):
        split = uri.split(":")
        def doAlbum(_id):
            tracks = client.album_tracks(_id)
            return tracks['total'], uri
            
        if split[1] == "playlist":
            playlist = client.playlist(split[2])
            
            num_tracks = playlist['tracks']['total']
            return num_tracks, uri
        elif split[1] == "artist":
            # Turn it into one of their albums
            raw = client.artist_albums(split[2])
            albums = raw['items']
            uri = random.choice(albums)['uri']
            return doAlbum(uri.split(":")[2])
        elif split[1] == "album":
            return doAlbum(split[2])

    def getName(str):
        ttype = str.split(":")[1]
        item = client.track(str) if ttype == 'track' \
            else client.album(str) if ttype == 'album' \
            else client.artist(str) if ttype == 'artist' \
            else client.playlist(str)
        return item['name']

    # Start playback
    def playMusic():
        if args.uri[0] == 'unset':
            dat = client.user_playlists("12144944831")['items']; # Get the playlists for my account
            dd = [o['id'] for o in dat]
            dd2 = [o['name'] for o in dat]
            choice = random.choice(dd)
            
            uuri = "spotify:playlist:{}".format(choice)
            num_tracks, uri = getTracks(uuri)
            
            print("♫ Playing " + dd2[dd.index(choice)] + " ♫")
            client.start_playback(device_id=spotify_device_id, context_uri=uuri, offset={"position": random.randint(0, num_tracks-1)})
            cast.wait()
            volume.setVolume(volume.MUSIC_VOLUME, "Spotify")
            client.shuffle(True, device_id=spotify_device_id)
        else:
            name = getName(args.uri[0])
            print("♫ Playing: " + name + " ♫")
            if args.uri[0].find("track") > 0:
                client.start_playback(device_id=spotify_device_id, uris=args.uri)
            else:
                num_tracks, uri = getTracks(args.uri[0])
                client.start_playback(device_id=spotify_device_id, context_uri=uri, offset={"position": random.randint(0, num_tracks-1)})
            volume.setVolume(volume.MUSIC_VOLUME, "Spotify")
            client.shuffle(True, device_id=spotify_device_id)
    playMusic()


def run():
    global args
    # Wait for cast device to be ready
    cast.wait()
    volume.read(args.msg)
    #read("It's time for bed. This is a really long message. Keep going. Let's see how far this can go.")
    play(args)
    
run()
# Shut down discovery
pychromecast.discovery.stop_discovery(browser)
sys.exit(0)
