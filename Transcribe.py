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
            'let it snow': 'Be101808700600500400100000',
            'baby it\'s cold outside': 'Be4006054008000000050070650080000000',
            'we\'re in the money':'Be608006708000000060800670800000',
            'home on the range': 'Be800000706005600000114000444003405000',
            'money': 'Bf5005095002004005007005005095002004005007005',
            'nobody home': 'Cf1160606666606000006600065605000',
            'quarter hour': 'Ha6541000',
            'half hour': 'Ha465104564000',
            'three quarter hour': 'Ha64510156406541000',
            'hour': 'Ha 4651045640645101564000000',
            'bong': '&4810000',
        }

    def act(self, data):
        print "SONG RECEIVED: ", datetime.datetime.now(), data
        song_data = json.loads(data)
        song = song_data.get('song','').lower()
        if song in self.songs:
            print "Playing song: ",song
            chime = self.songs[song]
            self.push_callback('chime', json.dumps({'tune':chime}))

