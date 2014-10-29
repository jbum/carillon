# Utils.py

# convert string (passed to service in kwargs via config file) to a proper bool
def parse_bool(v):
    return v in set(['True','true',True,1,'1','Yes','yes','On','on'])
