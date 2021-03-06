# Chime.py
#    Receives chime strings, and transmits them to the Arduino/Xbee.
#    A typical chime string looks like this: Bf1--5--4328--5--4328--5--4342  (star wars)
#      The two letters in front set the duration of each note in milliseconds 
#        (Uppercase letter is 100s of milliseconds and lowercase letter is 10s of milliseconds   Bf = 150 milliseconds)
#      The numbers represent note numbers (1 = pin 5, 2 = pin 6 etc).
#      Hyphens or 0s represent rests, and are used to extend the duration of notes.

from Action import Action
import json, datetime
import serial
from pytz import timezone
import time

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

    # not as simple as I would have liked, but for the Arduino/XBee, I have to slow down transmission so I don't overrun the buffer
    # this parses the protocol as it sends, and uses the same delays that are used in playback
    def sendStr(self, dataStr): 
        dataStr = dataStr.replace('-','0') # convert hyphens to 0s
        chDelay = 50.0 / 1000 # default delay
        chordMode = False
        xbee = serial.Serial(port=self.port,baudrate=self.baud)
        if not xbee.isOpen():
            xbee.open()
        for ch in dataStr:
            if ch >= 'A' and ch <= 'Z':
                chDelay = (ord(ch) - ord('A'))*100 / 1000.0
                if ch == 'A': # never send this - it's too fast
                    ch = 'B'
            elif ch >= 'a' and ch <= 'z':
                chDelay += (ord(ch) - ord('a'))*10 / 1000.0
            if ch == '0':
                chordMode = False
            elif ch == '&':
                chordMode = True
            useChDelay = ch == 0 or (ch in '123456789' and not chordMode)
            xbee.write(ch.encode('utf-8'))
            time.sleep(chDelay if useChDelay else 0.01)
        xbee.close()

    def act(self, data):
        print "CHIME RECEIVED: ", datetime.datetime.now(), data
        chime_data = json.loads(data)
        chime_tune = chime_data.get('tune','0')
        print "Tune: ",chime_tune

        # open serial connection and send the chime...
        # this will work with an arduino, or an xbee talking to an arduino
        if not self.is_muted():
            self.sendStr(chime_tune)
        else:
            print "Muted - ignoring chime"
