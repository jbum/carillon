from Action import Action
import json, datetime, time
from Utils import parse_bool
from pytz import timezone

class Clock(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        self.ring_quarters = parse_bool(kwargs.get('ring_quarters', False))
        self.timezone = kwargs.get('timezone', 'America/Los_Angeles')
        self.chimes = {
            'hour':'Fa 4 6 5 1 0 4 5 6 4 0 6 4 5 1 0 1 5 6 4 0 0 0 0 0 0',
            '1/4':'Fa 6 5 4 1 0 0 0',
            '1/2':'Fa 4 6 5 1 0 4 5 6 4 0 0 0',
            '3/4':'Fa 6 4 5 1 0 1 5 6 4 0 6 5 4 1 0 0 0',
            'bong':'Ta &481 0 0',
        }
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
            # chime the appropriate quarter hour
            if minute == 59 or minute == 0 or minute == 1:
                chime = self.chimes['hour']
                hour = now.hour % 12
                if hour == 0:
                    hour = 12
                chime += (self.chimes['bong'] * hour)
            elif self.ring_quarters:
                if minute >= 14 and minute <= 16:
                    chime = self.chimes['1/4']
                elif minute >= 29 and minute <= 31:
                    chime = self.chimes['1/2']
                elif minute >= 44 and minute <= 46:
                    chime = self.chimes['3/4']
            if chime != '':
                self.push_callback('chime', json.dumps({'tune':chime}))

            now = datetime.datetime.now()
            now = localtz.localize(now)

            print "Clock Now",now
            if minute < 45:
                nextTime = now.replace(minute=15*(int(now.minute/15)+1),second=0,microsecond=0)
            else:
                nextTime = now.replace(hour=now.hour+1,minute=0,second=0,microsecond=0)
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

