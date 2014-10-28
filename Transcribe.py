from Action import Action
import json, datetime

# Transcribe song names to tunes

class Transcribe(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        self.start()

        # Actual Notes:  D  E  F# G  A  B  C  D  E
        # In C        :  G  A  B  C  D  E  F  G' A'
        #                1  2  3  4  5  6  7  8  9   

        # spaces are ignored

        # Aa (Upper case followed by lowercase) is used to set delay between notes in milliseconds - always provide both letters
        #    Upper case letter is 100s unit  (A=0, B=100, C=200, etc.)
        #    Lower case letter is 10s unit   (a=0, b=10, c=20)
        #    Example: Fa is 500 milliseconds, Fb is 510 milliseconds, Ta is 2 seconds
        #    Minimum delay is 50 ms

        # 1-9 are note numbers  0 is a delay (each node value gets an implicit delay, unless in chord mode)
        # & puts us in chord mode (no delay til next 0, then all pins reset, and we go back into single mode)
        # In single note mode (the default), each note value gets an implicit delay.

        self.songs = {
            'let it snow': 'Be 1 0 1 8 0 8 7 0 0 6 0 0 5 0 0 4 0 0 1 0 0 0 0 0',
            'baby it\'s cold outside': 'Be 4 0 0 6 0 5 4 0 0 8 0 0 0 0 0 0 0 5 0 0 7 0 6 5 0 0 8 0 0 0 0 0 0 0',
            'we\'re in the money':'Be 6 0 8 0 0 6 7 0 8 0 0 0 0 0 0 0 6 0 8 0 0 6 7 0 8 0 0 0 0 0',
            'home on the range': 'Be 8 0 0 0 0 0 7 0 6 0 0 5 6 0 0 0 0 0 1 1 4 0 0 0 4 4 4 0 0 3 4 0 5 0 0 0',
            'money': 'Bf 5 0 0 5 0 9 5 0 0 2 0 0 4 0 0 5 0 0 7 0 0 5 0 0 5 0 9 5 0 0 2 0 0 4 0 0 5 0 0 7 0 0 5',
            'nobody home': 'Cf 1 1 6 0 6 0 6 6 6 6 6 0 6 0 0 0 0 0 6 6 0 0 0 6 5 6 0 5 0 0 0',
            'quarter hour': 'Ha 6 5 4 1 0 0 0',
            'half hour': 'Ha 4 6 5 1 0 4 5 6 4 0 0 0',
            'three quarter hour': 'Ha 6 4 5 1 0 1 5 6 4 0 6 5 4 1 0 0 0',
            'hour': 'Ha 4 6 5 1 0 4 5 6 4 0 6 4 5 1 0 1 5 6 4 0 0 0 0 0 0',
            'bong': 'Ha &481 0 0 0 0',
        }

    def act(self, data):
        print "SONG RECEIVED: ", datetime.datetime.now(), data
        song_data = json.loads(data)
        song = song_data.get('song','').lower()
        if song in self.songs:
            print "Playing song: ",song
            chime = self.songs[song]
            self.push_callback('chime', json.dumps({'tune':chime}))

