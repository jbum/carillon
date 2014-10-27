from Action import Action
import json, datetime
import serial
from pytz import timezone

class Chime(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        # settings for XBee radio connect -- set up in site.cfg, or override in local-site.cfg
        self.port = kwargs.get('port', "/dev/tty.usbmodem1431")
        self.baud = int(kwargs.get('baud', 9600))
        self.start_mute = int(kwargs.get('start_mute', 0)) # HHMM
        self.end_mute = int(kwargs.get('end_mute', 0)) # HHMM
        self.start()
        self.timezone = kwargs.get('timezone', 'America/Los_Angeles')

    def is_muted(self):
        if self.start_mute == 0 and self.end_mute == 0:
            return False
        localtz = timezone(self.timezone)
        now = datetime.datetime.now()
        now = localtz.localize(now)
        hhmm = int("%02d%02d" % (now.hour,now.minute))
        if self.end_mute > self.start_mute:
            return hhmm >= self.start_mute and hhmm < self.end_mute
        else:
            return hhmm >= self.start_mute or hhmm < self.end_mute

    def act(self, data):
        print "CHIME RECEIVED: ", datetime.datetime.now(), data
        chime_data = json.loads(data)
        chime_tune = chime_data.get('tune','0')
        print "Tune: ",chime_tune

        # open serial connection and send the chime...
        # this will work with an arduino, or an xbee talking to an arduino
        if not self.is_muted():
            xbee = serial.Serial(port=self.port,baudrate=self.baud)
            if xbee.isOpen():
                xbee.close()
            xbee.open()
            xbee.write(chime_tune)
            xbee.close()
        else:
            print "Muted - ignoring chime"
