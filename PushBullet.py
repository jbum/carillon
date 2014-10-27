from Action import Action
import json, datetime, threading
from ws4py.client.threadedclient import WebSocketClient

class PBClient(WebSocketClient):
    def opened(self):
        print "PB Connection opened"

    def closed(self, code, reason=None):
        print "PB Closed down", code, reason
        # !! wait 15 seconds, and reopen?

    def received_message(self, m):
        print "PB Received",m
        mrec = json.loads(str(m))
        if mrec['type'] == 'note':
            self.pb.push_callback('pushbullet', json.dumps(mrec))
        elif mrec['type'] == 'tickle':
            print "Tickle"
            # get latest pushes, and process them...

    def set_parent(self, pb):
        self.pb = pb

class PBThread(threading.Thread):
    def __init__(self, access_token, parent):
       threading.Thread.__init__(self)
       self.ws = PBClient('wss://stream.pushbullet.com/websocket/' + access_token, protocols=['http-only', 'chat'])
       self.ws.set_parent(parent)

    def run(self):
        try:
            self.ws.connect()
            self.ws.run_forever()
        except KeyboardInterrupt:
            self.ws.close()

class PushBullet(Action):
    def __init__(self, **kwargs):
        Action.__init__(self, **kwargs)
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
            if 'tune:' in mrec['body']:
                chime = mrec['body'][:5].strip()
                self.push_callback('chime', json.dumps({'tune':chime}))
            elif 'song:' in mrec['body']:
                song = mrec['body'][:5].strip()
                self.push_callback('transcribe', json.dumps({'song':song}))
