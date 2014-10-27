from Action import Action
import json, datetime

class Chime(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        # settings for XBee radio connect
        self.port = kwargs.get('port', "/dev/tty.usbmodem1431")
        self.baud = int(kwargs.get('baud', 9600))

        self.start()

    def act(self, data):
        print "CHIME RECEIVED: ", datetime.datetime.now(), data
        chime_data = json.loads(data)
        chime_tune = chime_data.get('tune','0')
        print "Tune: ",chime_tune
        # !! open serial connection and send the chime...
