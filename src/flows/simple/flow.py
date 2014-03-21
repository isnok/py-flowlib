from flib.flow import expose

@expose("alias")
def aliased():
    # an undocumented command
    print "this is aliased"

@expose
def aliased():
    """A documented command"""
    print "this is weird"
