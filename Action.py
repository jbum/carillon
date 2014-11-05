from abc import ABCMeta, abstractmethod
from threading import Thread, Event, Lock
from time import sleep
import traceback
import sys

def xor_strings(s,t):
    """xor two strings together"""
    return "".join(chr(ord(a)^ord(b)) for a,b in zip(s,t))

def hardware(hardware_function):
    '''Decorator to allow hardware based functions to be skipped if running 
    without it being connected to the machine.'''
    def hardware_decorator(*args):
        instance = args[0]
        if instance.valid_hardware:
            return hardware_function(*args)
        else:
            return
    return hardware_decorator

def context(web_function):
    '''Decorator to provide a context for the flask web application.'''
    def added_context(*args):
        instance = args[0]
        with instance.web_context:
            return web_function(*args)
    return added_context

def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    traceback.print_exception(exc_type, exc_obj, tb)


class Action(Thread):
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        Thread.__init__(self)

        self._stop = Event()
        self.daemon = True
        self.message_list = []
        self.data_lock = Lock()

        # Always defined kwargs:
        #   name: self described name of the action
        #   subscribe: the topic the action is called with
        #   push_callback: callback function to push a message with JSON
        #   hardware: if valid hardware is present (assume true if missing)
        #   context: a generic (test) context for the flask application
        self.name = kwargs['name']
        self.subscribe = kwargs['subscribe']
        self.push_callback = kwargs['push_callback']
        self.web_context = kwargs['web_context']
        self.valid_hardware = bool(kwargs.get('hardware', True))

    def __del__(self):
        self.stop()
        self.join()

    def stopped(self):
        return self._stop.isSet()

    def stop(self):
        self._stop.set()

    def start_second_thread(self):
        t2 = Thread(target=self.kickoff_async)
        t2.start()
        # pbt2 = SecondaryThread(self)
        # pbt2.start()

    @abstractmethod
    def act(self, data):
        '''Called each time a message is ready.'''
        pass

    def kickoff(self):
        '''Called once just as the server stats up.'''
        pass

    def kickoff_async(self):
        '''Called for modules that need a 2nd thread.'''
        pass

    def run(self):
        '''Threaded, runs actions on each message.'''
        while not self.stopped():
            sleep(0.25)
            if len(self.message_list) > 0:
                self.data_lock.acquire()
                data = self.message_list.pop(0)
                self.data_lock.release()

                #print "ACT", self.name
                try:
                    self.act(data)
                except Exception as ex:
                    print "=== ERROR ACTING:", self.name
                    print ex
                    print_exception()


    def publish(self, message):
        self.data_lock.acquire()
        self.message_list.append(message)
        self.data_lock.release()

    def subscribe(self, message):
        pass