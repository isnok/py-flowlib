from flib.flow import expose
from flib.args import args

@expose("alias")
def aliased():
    # an undocumented command
    print "this is aliased"
    if args.debug:
        print "You're in debug, and i know it."

@expose
def aliased():
    """A documented command"""
    print "this is weird"
