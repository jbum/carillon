from Action import Action
import json, datetime

# Transcribe song names to tunes

class Transcribe(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        self.start()

        self.songs = {
            'let it snow': 'Da 1 1 8 8 7 0 6 0 5 0 4 0 1 0 0 0',
            'baby it\'s cold outside': 'Da 4 0 6 5 4 0 8 0 0 0 0 0 5 0 7 6 5 0 8 0 0 0 0 0',
            'we\'re in the money':'Da 4 0 6 0 0 4 5 0 6 0 0 0 0 0 0 0 4 0 6 0 0 4 5 0 6 0 0 0 0 0',
            'home on the range': 'Da 8 0 0 0 0 0 7 0 6 0 0 5 6 0 0 0 0 0 1 1 4 0 0 0 4 4 4 0 0 3 4 0 5 0',
            'nobody home': 'Da 1 1 6 0 6 0 6 6 6 6 6 0 6 0 0 0 0 0 6 6 0 0 0 6 5 6 0 5 0 0 0',
            'quarter hour': 'Fa 6 5 4 1 0 0 0',
            'half hour': 'Fa 4 6 5 1 0 4 5 6 4 0 0 0',
            'three quarter hour': 'Fa 6 4 5 1 0 1 5 6 4 0 6 5 4 1 0 0 0',
            'hour': 'Fa 4 6 5 1 0 4 5 6 4 0 6 4 5 1 0 1 5 6 4 0 0 0 0 0 0',
            'bong': 'Ta &481 0 0',
        }

    def act(self, data):
        print "SONG RECEIVED: ", datetime.datetime.now(), data
        song_data = json.loads(data)
        song = song_data.get('song','').lower()
        if song in self.songs:
            print "Playing song: ",song
            chime = self.songs[song]
            self.push_callback('chime', json.dumps({'tune':chime}))

