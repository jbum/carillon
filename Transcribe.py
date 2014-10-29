from Action import Action
import json, datetime

# Transcribe song names to tunes

class Transcribe(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        self.songs = json.loads(kwargs.get('songs',"{}"))
        print "Got Songs", self.songs
        self.start()

    def act(self, data):
        print "SONG RECEIVED: ", datetime.datetime.now(), data
        song_data = json.loads(data)
        song = song_data.get('song','').lower()
        if song in self.songs:
            print "Playing song: ",song
            chime = self.songs[song]
            self.push_callback('chime', json.dumps({'tune':chime}))

