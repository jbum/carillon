from Action import Action
import json, datetime
import ConfigParser

# Transcribe song names to tunes

class Transcribe(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        config = ConfigParser.SafeConfigParser()
        config.read(['site.cfg','local-site.cfg']) # songs are loaded from config file...
        self.songs = dict(config.items('songs'))
        self.start()

    def act(self, data):
        print "SONG RECEIVED: ", datetime.datetime.now(), data
        song_data = json.loads(data)
        song = song_data.get('song','').lower()
        if song in self.songs:
            print "Playing song: ",song
            chime = self.songs[song]
            self.push_callback('chime', json.dumps({'tune':chime}))

