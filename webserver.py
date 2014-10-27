#!/usr/bin/python

import sys
import time
from flask import (Flask, Response, abort, render_template, json, request, 
    make_response, current_app, jsonify)
import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue
from Action import Action
from ServerSentEvent import ServerSentEvent
from datetime import timedelta
from functools import update_wrapper
import re
import ConfigParser
import os.path
import dateutil.parser
import datetime
from pytz import timezone

# Webserver setup
webapp = Flask(__name__)
# webapp.secret_key = 'asf45yaergsetrgw'

@webapp.errorhandler(404)
@webapp.errorhandler(403)
@webapp.errorhandler(500)
def error_page(error):
    '''Some generic error handlers.'''
    message = "There was a problem processing the request."
    return render_template("error.html", brand=brand, title=error, 
        navigation=pages, error_message=message, author=author), error.code

@webapp.errorhandler(Exception)
def exception_page(error):
    '''Catch-all exception handler.'''
    if webapp.debug:
        raise
    else:
        abort(500)

@webapp.route('/')
def index():
    '''Index root page.'''
    return render_template("index.html", 
        brand=brand, title=brand, navigation=pages, author=author)

@webapp.route("/debug")
def debug():
    '''Debug for testing purposes.'''
    if webapp.debug:
        return "Currently %d subscriptions" % len(subscriptions)
    else:
        abort(403)

@webapp.route('/dochime/<tune>')
def dochime(tune):
    result = {'success':True,'tune':tune}
    push_event('chime', json.dumps({'tune':tune}))

    # post this user to the event stream...   
    return jsonify(result)

@webapp.route('/dosong/<song>')
def dosong(song):
    result = {'success':True,'song':song}
    push_event('transcribe', json.dumps({'song':song}))
    # post this user to the event stream...   
    return jsonify(result)


@webapp.route('/<topic>')
def navigation(topic):
    '''Topics created by the pages configuration.'''
    if topic in pages:
        return render_template("%s.html" % topic,
            brand=brand, title=pages[topic], navigation=pages, author=author)
    else:
        abort(404)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def event_stream(topic):
    '''Publishes events based on the topic.'''
    q = Queue()
    subscriptions[topic].append(q)
    try:
        while True:
            try:
                result = q.get_nowait()
            except gevent.queue.Empty:
                gevent.sleep(1)
                continue
            ev = ServerSentEvent(str(result))
            yield ev.encode()
    except GeneratorExit:
        subscriptions[topic].remove(q)
    except Exception as ex:
        print "Generic event-stream exception!"
        print ex
        subscriptions[topic].remove(q)

def push_event(topic, data):
    '''Callback for python actions to re-publish new data.'''
    if topic not in subscriptions:
        print "Topic %s not in subscriptions" % (topic)
    else:
        for sub in subscriptions[topic]:
            sub.put(data)

    # Run any related python action if possible
    if actions.get(topic, None):
        actions[topic].publish(data)
    print "PUSH", topic
    sys.stdout.flush()

@webapp.route('/subscribe/<topic>')
@crossdomain(origin='*')
def subscribe(topic):
    '''Subscribes clients to specific topics.'''
    if topic in pages:
        return Response(event_stream(topic), mimetype="text/event-stream")
    else:
        abort(404)


@webapp.route('/publish/<topic>', methods=['POST'])
@crossdomain(origin='*')
def publish(topic):
    '''Publishes client POST data to the topics.'''
    if request.method == 'POST' and topic in subscriptions:
        # Convert the POST data to a dictionary and add the server time
        req_dict = request.form.to_dict()
        req_dict['servertime'] = time.strftime("%Y-%m-%d %H:%M:%S")
        message = json.dumps(req_dict)

        # Push the event to clients
        #push_event(topic, message)
        gevent.spawn(lambda: push_event(topic, message))

        return Response(status=204)
    else:
        abort(404)

# Read configuration
print "SETUP STARTING"
print "TIME: ", datetime.datetime.now()

config = ConfigParser.SafeConfigParser()

config.read(['site.cfg','local-site.cfg'])

brand = config.get('website', 'brand')
author = config.get('website', 'author')
pages = {}
subscriptions = {}
actions = {}
for page, enable in config.items("pages"):
    # Check if the page is enabled
    if not config.getboolean('pages', page):
        continue

    settings = dict(config.items(page))

    # Set the page name
    if 'name' in settings:
        pages[page] = settings['name']
    else:
        settings['name'] = page
        pages[page] = page

    # Add a subscription endpoint if requested
    if 'subscribe' in settings:
        topic = settings['subscribe']
        subscriptions[topic] = []

        print "PAGE TOPIC:", topic

        # Dynamically load python action for each subscription topic
        if 'action' in settings:
            try:
                action = settings['action']
                exec("import %s" % action)
                action_object = sys.modules[action].__dict__[action]

                # Make sure the object has the right type
                if not issubclass(action_object, Action):
                    raise Exception("Action object must be subclass of Action")

                # Add some extra kwargs
                settings['push_callback'] = push_event
                settings['web_context'] = webapp.test_request_context()

                # Create an object passing all the settings as arguments
                actions[topic] = action_object(**settings)
            except Exception as ex:
                actions[topic] = None
                print "Unable to load actions for %s." % action
                raise
        else:
            actions[topic] = None

# Run kickoff functions
for topic in pages:
    if actions.get(topic, None):
        actions[topic].kickoff()

if __name__ == "__main__":
    host = config.get('website', 'host')
    port = config.getint('website', 'port')
    webapp.debug = config.getboolean('website', 'debug')
    webapp.threaded = True # attempt to reduce intermittent 'broken pipe' errors http://stackoverflow.com/questions/12591760/flask-broken-pipe-with-requests
    if webapp.debug:
        print "DEBUG MODE! WILL RAISE ERRORS!"

    print "SETUP DONE. Starting server at http://%s:%s/" % (host,port)
    print "TIME: ", datetime.datetime.now()
    sys.stdout.flush()
    server = WSGIServer((host, port), webapp)
    from gevent import monkey
    monkey.patch_all()
    server.serve_forever()
    #webapp.run(host=host, port=port, debug=debug, threaded=True)
