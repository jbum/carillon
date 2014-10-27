from Action import Action
import json, datetime, threading
from ws4py.client.threadedclient import WebSocketClient
import requests

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
        if mrec['type'] == 'note':
            self.pb.push_callback('pushbullet', json.dumps(mrec))
        elif mrec['type'] == 'tickle':
            print "Tickle"
            # get latest pushes, and process them...
            self.pull_pb_pushes()

    def do_init(self, pb, access_token):
        self.pb = pb
        self.access_token = access_token
        self.last_pb_ts = 0.0
        self.mute_pushes = True
        self.pull_pb_pushes() # pull last set of pushes, so we can determine last timestamp
        self.mute_pushes = False

class PBThread(threading.Thread):
    def __init__(self, access_token, parent):
       threading.Thread.__init__(self)
       self.ws = PBClient('wss://stream.pushbullet.com/websocket/' + access_token, protocols=['http-only', 'chat'])
       self.ws.do_init(parent, access_token)

    def run(self):
        try:
            self.ws.connect()
            self.ws.run_forever()
        except KeyboardInterrupt:
            self.ws.close()

class PushBullet(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)

        # Push Bullet settings -- set up in site.cfg, or override in local-site.cfg
        self.access_token = kwargs.get('access_token', "XXX")
        self.start()

    def kickoff(self):
        # kick off thread...
        self.pbThread = PBThread(self.access_token, self)
        self.pbThread.daemon = True
        self.pbThread.start()

    def act(self, data):
        print "PUSHBULLET RECEIVED: ", datetime.datetime.now(), data
        mrec = json.loads(data)
        if mrec['type'] == 'note':
            if 'tune:' in mrec['body']: # 'tune' uses the low-level protocol which goes straight to 'chime' handler
                chime = mrec['body'][5:].strip()
                self.push_callback('chime', json.dumps({'tune':chime}))
            elif 'song:' in mrec['body']: # 'song' is a song-title which is converted to low-level protocol by 'transcribe' handler
                song = mrec['body'][5:].strip()
                self.push_callback('transcribe', json.dumps({'song':song}))
