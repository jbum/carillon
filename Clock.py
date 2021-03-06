# Clock.py
# Wakes up every quarter hour and plays an appropriate chime, like a grandfather clock.  
# The chime melodies used for each quarter are defined in site.cfg.

from Action import Action
import json, datetime, time
from Utils import parse_bool
from pytz import timezone

class Clock(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        # clock settings -- set up in site.cfg, or override in local-site.cfg
        self.ring_quarters = parse_bool(kwargs.get('ring_quarters', False))
        self.xmas_mode = parse_bool(kwargs.get('xmas_mode', False))
        self.timezone = kwargs.get('timezone', 'America/Los_Angeles')
        self.chimes = json.loads(kwargs.get('chimes',"{}"))
        self.xmas_hours =  json.loads(kwargs.get('xmas_hours',"[]"))
        print "Got chimes", self.chimes
        print "Got xmas_hours", self.xmas_hours

        self.start()

    def kickoff(self):
        self.push_callback("clock",json.dumps({"type":"kickoff"}))

    def act(self, data):
        print "CLOCK RECEIVED: ", datetime.datetime.now(), data
        while True:
            localtz = timezone(self.timezone)
            now = datetime.datetime.now()
            now = localtz.localize(now)

            minute = now.minute
            chime = ''
            song = ''
            # chime the appropriate quarter hour
            if minute == 0:
                if self.xmas_mode:
                    song = self.xmas_hours[now.hour % len(self.xmas_hours)]
                else:
                    chime = self.chimes['hour']
            elif self.ring_quarters:
                if minute  == 15:
                    chime = self.chimes['1/4']
                elif minute == 30:
                    chime = self.chimes['1/2']
                elif minute == 45:
                    chime = self.chimes['3/4']
            if chime != '':
                self.push_callback('chime', json.dumps({'tune':chime}))
                if minute == 0:
                    hour = now.hour % 12
                    if hour == 0:
                        hour = 12
                    chime = (self.chimes['bong'] * hour)
                    self.push_callback('chime', json.dumps({'tune':chime}))
            elif song != '':
                self.push_callback('transcribe', json.dumps({'song':song}))

            now = datetime.datetime.now()
            now = localtz.localize(now)

            print "Clock Now",now
            if minute < 45:
                nextTime = now.replace(minute=15*(int(now.minute/15)+1),second=0,microsecond=0)
            else:
                nextTime = now.replace(minute=0,second=0,microsecond=0)+datetime.timedelta(hours=1)
            print "Clock Next: ",nextTime
            delta = (nextTime - now)
            print "Sleep Delta",delta
            sleep_secs = delta.seconds+1 # add a second to account for rounding error
            if sleep_secs < 0 or sleep_secs > 901: # should never happen, try again in 5 minutes
                sleep_secs = 60*5
            print "Clock Sleeping Secs",sleep_secs
            try:
                time.sleep(  sleep_secs )
            except KeyboardInterrupt:
                break

