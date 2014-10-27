# Utils.py
import traceback
import sys

def parse_bool(v):
    return v in set(['True','true',True,1,'1','Yes','yes','On','on'])


def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    traceback.print_exception(exc_type, exc_obj, tb)

