from Action import Action
import json, datetime

class Transcribe(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        self.start()

    def act(self, data):
        print "TRANSCRIBE RECEIVED: ", datetime.datetime.now(), data

        # transcribe high level to low level message, and call chime
