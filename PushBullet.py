# PushBullet.py
#
# Subscribes to incoming messages from the PushBullet service (which in turn, can receive events from IFTTT, or from your laptop or phone).
#
# Messages of type 'note' which contain a body that begins with tune: are sent to the Chime service.
# Messages of type 'note' which contain a body that beings with song: are sent to the Transcription service.
# (both of the above can be created in IFTTT)
#
# A set of additional triggers is defined in site.cfg for matching incoming 'push' messages, 
# which are typically seen for emails and SMS messages.

from Action import Action
import json, datetime
from ws4py.client.threadedclient import WebSocketClient
import requests
import json
import calendar, time

class PBClient(WebSocketClient):
    def opened(self):
        print "PB Connection opened"

    def closed(self, code, reason=None):
        print "PB Closed down", code, reason
        # !! wait 15 seconds, and reopen?

    def pull_pb_pushes(self):
        url = 'https://api.pushbullet.com/v2/pushes?modified_after=' + str(self.last_pb_ts)
        client = requests.session()
        print "Retrieving PB Pushes"
        r = client.get(url,headers={'Authorization':'Bearer ' + self.access_token})
        recArray = r.json()
        for mrec in recArray['pushes']:
            modTS = float(mrec['modified'])
            if modTS > self.last_pb_ts:
                self.last_pb_ts = modTS
                if not self.mute_pushes:
                    print "PBPUSH",mrec['type'],mrec['title'],mrec['modified']
                    self.pb.push_callback('pushbullet', json.dumps(mrec))

    def received_message(self, m):
        print "PB Received",m
        mrec = json.loads(str(m))
        if mrec['type'] == 'note' or mrec['type'] == 'push':
            self.pb.push_callback('pushbullet', json.dumps(mrec))
        elif mrec['type'] == 'tickle':
            print "Tickle"
            # get latest pushes, and process them...
            self.pull_pb_pushes()

    def do_init(self, pb, access_token):
        self.pb = pb
        self.access_token = access_token
        self.last_pb_ts = calendar.timegm(time.gmtime()) - 60*60*24
        self.mute_pushes = True
        self.pull_pb_pushes() # pull last set of pushes, so we can determine last timestamp
        print "Last PB Time stamp:",self.last_pb_ts
        self.mute_pushes = False

class PushBullet(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        # Push Bullet settings -- set up in site.cfg, or override in local-site.cfg
        self.access_token = kwargs.get('access_token', "XXX")
        self.triggers = json.loads(kwargs.get('triggers',"[]"))
        print "Got Triggers: ",self.triggers
        self.start()

    def kickoff_async(self):
        ws = PBClient('wss://stream.pushbullet.com/websocket/' + self.access_token, protocols=['http-only', 'chat'])
        ws.do_init(self, self.access_token)
        try:
            ws.connect()
            ws.run_forever()
        except KeyboardInterrupt:
            ws.close()

    def act(self, data):
        print "PUSHBULLET RECEIVED: ", datetime.datetime.now(), data
        mrec = json.loads(data)
        if mrec['type'] == 'note' and ('tune:' in mrec['body'] or 'song:' in mrec['body']):
            if 'tune:' in mrec['body']: # 'tune' uses the low-level protocol which goes straight to 'chime' handler
                chime = mrec['body'][5:].strip()
                self.push_callback('chime', json.dumps({'tune':chime}))
            elif 'song:' in mrec['body']: # 'song' is a song-title which is converted to low-level protocol by 'transcribe' handler
                song = mrec['body'][5:].strip()
                self.push_callback('transcribe', json.dumps({'song':song}))
        else:
            # triggers = [{"song": "glissando", "type": "push", "contains": "Web Tools"}, 
            #             {"song": "darkside", "type": "push", "contains": "Demo Update"}]
            for trig in self.triggers:
                if mrec['type'] == trig['type']:
                    gotMatch = False
                    if mrec['type'] == 'push':
                        if 'body' in mrec['push'] and 'contains' in trig and trig['contains'].lower() in (mrec['push']['body'] + ' ' + mrec['push']['title']).lower():
                            gotMatch = True
                    if gotMatch:
                        if 'song' in trig:
                            self.push_callback('transcribe', json.dumps({'song':trig['song']}))
                        elif 'tune' in trig:
                            self.push_callback('chime', json.dumps({'tune':trig['tune']}))

