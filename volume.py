from urllib.parse import urlparse
import pychromecast
import time
import random
import types

SPEECH_VOLUME = 0.9999
MUSIC_VOLUME = 0.6
# terminate = False
cast = None

def init(castt):
    global cast
    cast = castt

def almost_equal(x, y, delta=0.001):
    print(abs(x-y))
    return abs(x-y) < delta
    
def waitUntilActive(target="Default Media Receiver"):
    while cast.status.display_name != target:
        time.sleep(0.3)
    
def setVolume(level, target="Default Media Receiver"):
#    cast.set_volume(0.5)
#     state = cast.media_controller.status
#     active = cast.status.display_name
#     last = 0
#     current = cast.media_controller.status.last_updated
#     i = 0
#     while (last == current or not state.supports_stream_volume or state.player_state != "PLAYING" or target != active) and i < 15:
#         last = state.last_updated
#         time.sleep(0.03)
#         state = cast.media_controller.status
#         active = cast.status.display_name
#         current = state.last_updated
#         ++i
        
#     print(cast.status)
#     cast.set_volume(level)
#     volSet = False
#     player_state = "PLAYING"
#     default = True
#     while not volSet:
#         if last != current:
#             if player_state != cast.media_controller.status.player_state:
#                 player_state = cast.media_controller.status.player_state
#                 default = False
#                 print(player_state)
#                 
#             if cast.status.display_name == target:
#                 cast.set_volume(level)
#                 volSet = not default and cast.media_controller.status.supports_stream_volume \
#                     and player_state == "PLAYING"
#         time.sleep(0.03)
#         last = current
#         current = cast.media_controller.status.last_updated

    volSet = False
    while not volSet:
#         print("{} ... {}".format(cast.status.display_name, cast.media_controller.status.current_time))
        volSet = cast.status.display_name == target and cast.media_controller.status.current_time > 0.1
        time.sleep(0.03)
    cast.set_volume(level)
    print(cast.device.friendly_name + " volume set to {}".format(level))
    
def read(text):
    cast.wait()
#     cast.start_app("CC1AD845") # Launch Media Receiver so we can actually set the volume.
#     cast.wait()
    mc = cast.media_controller
    dblink = urlparse("http://translate.google.com/translate_tts?ie=UTF-8&total=1&idx=0&textlen=32&client=tw-ob&q=" + text + "&tl=en-us").geturl()
    print("Reading '" + text + "'")
    mc.play_media('http://10.0.0.197/silence.mp3', 'audio/mp3')
    setVolume(SPEECH_VOLUME)
    mc.play_media(dblink, 'audio/mp3')
    
    #Wait for the media to actually play
    player_state = None
    has_played = False
    played_full = False
    t = 30
    first = True
    while not played_full:
        try:
            if first:
                player_state = "IDLE"
                first = False
                time.sleep(0.3)
                t -= 0.3
                continue
            if player_state != cast.media_controller.status.player_state:
                player_state = cast.media_controller.status.player_state
                #print("Player state:", player_state)
                if player_state == "PLAYING":
                    has_played = True
                if player_state == "UNKNOWN":
                    has_played = False #If it says 'UNKNOWN' we'll assume it didn't work.
                    
                if has_played and cast.media_controller.status.player_state == "IDLE":
                    played_full= True
#                 if played_full:
#                     terminatePlayback()
                #loop
                #if cast.socket_client.is_connected and has_played and player_state != "PLAYING":
                #    has_played = False
                #    cast.media_controller.play_media(args.url, "audio/mp3")

            time.sleep(0.1)
            t = t - 0.1
        except KeyboardInterrupt:
            print("Broke")
            break
    
# def terminatePlayback():
#     global terminate
#     terminate = True

# async def setFreakingVolume(level):
#     global cast
#     if cast == None:
#         print("No Chromecast set! Use init()")
#         return
#     
#     level = MUSIC_VOLUME if level == "music" else SPEECH_VOLUME
#     global terminate
#     terminate = False
#     i = 150
#     last = 0.001
#     while i > 0 and not terminate:
#         i -= 1
#         print("Device: {}".format(cast.device))
#         print("Status: {}".format(cast.status))
#         if cast.media_controller != None:
#             print("Media: {}".format(cast.media_controller.status))
#         print()
#         print()
#         cast.wait()
#         diff = 0 if last == 0.001 else 0.001
#         last = diff
#         cast.set_volume(level - diff)
#         await asyncio.sleep(0.05)
#     cast.set_volume(level)
#     if terminate:
#         print("Terminated task.")
#     terminate = False
# def setFreakingVolumeNice(level):
#     global cast
#     global terminate
#     if cast == None:
#         print("No Chromecast set! Use init()")
#         return
#     
#     print("Device: {}".format(cast.device))
#     print("Status: {}".format(cast.status))
#     if cast.media_controller != None:
#         print("Media: {}".format(cast.media_controller.status))
#     print()
#     print()
#     
#     level = MUSIC_VOLUME if level == "music" else SPEECH_VOLUME
#     cast.wait()
#     diff = 0
#     if random.randint(0,2) > 0:
#         diff = 0.001
#     cast.set_volume(level - diff)
#     if terminate:
#         print("Terminated")
#         terminate = False