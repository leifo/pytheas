# lxo, 20.06.2008
# determine if running on a phone or desktop
# and (more importantly) add import paths accordingly

'''
After importing this module from your code, you have the following benefits:
- variable g_isPhone is set to True (real phone, or emulator) or False (desktop Python)

- variable g_isRealPhone is set to True (Nokia Python S60 on actual hardware) or False (everything else)

- Amiga style assigns are available to deal with paths in a homogenous way.
    you can define virtual volume names to point to absolute paths
    when moving data around, you only have to change one assign, rather than all absolute paths in your code
    as a hook to the world, the path of the currently running script is assigned to be "PROGDIR:"
    so loading from a subdirectory can be done via, e.g. "PROGDIR:idata/example1_dat.txt"
    instead of qualifying the full path, e.g. "e:/python/idata/example1_dat.txt"
    this is especially handy as Symbian OS does not have a notion of paths, i.e. you would otherwise
    have to always use absolute paths, which is a bad style

See example1-bootstrap.py for an example of how to use it.
'''

# lxo, 03.07.2008
# now also supports virtual volume names through assigns (see modules/assigns.py)
#  e.g. "progdir:file" where "progdir:" is the assign which will be resolved to its actual path
#  by calling assign("progdir:file")

# lxo, 08.07.2008
# added support for PyS60 emulator
# added g_isRealPhone variable

# sets g_isPhone to True if on phone (i.e. PyS60 on phone or emulator), otherwise False (e.g. PC)
# sets g_isRealPhone to True if on real phone (PyS60), otherwise False (PyS60 emulator)

import sys

#--- custom import paths
def addImportPath(path, debug=False):
    # already in search path?
    if path in sys.path:
        if debug: print "***Debug: known dynamic import path:", path
    else:
        sys.path.append(path)
        if debug: print "***Debug: added dynamic import path:", path

#--- phone or desktop
g_isPhone=None
try:
    import e32
    g_isPhone=True
except:
    g_isPhone=False

#print "g_isPhone: %s" %(g_isPhone)
g_isRealPhone= False
#--- add import paths accordingly
if g_isPhone:
    g_isRealPhone = not e32.in_emulator()
    try:
        # for Series 60 we need full paths (no concept of current directory)
        if not g_isRealPhone:
            # emulator stores python scripts in c:\python (which is 'Epoc32\winscw\c\python\')
            addImportPath("C:\\Python\\modules")
            addImportPath("C:\\Python")
        else:
            # on phones the scripts are stored on the memory card
            addImportPath("E:\\Python\\modules")
            addImportPath("E:\\Python")
    except:
        pass
else:
    try:
        # for desktop we can just add in a relative way
        addImportPath("modules")
    except:
        pass

#--- platform specific implementations of common functions
if g_isPhone:
    def wait(secs):
        e32.ao_sleep(secs)
else:
    import time
    def wait(secs):
        time.sleep(secs)

#--- add assigns
from assigns import *
# "progdir:", where the application was started from
if g_isPhone:
##    import appuifw
##    fullName = appuifw.app.full_name()
##    appPath = fullName[0:fullName.rfind('\\')+1]
##    print appPath
    # above would be the proper way for installed apps that came from a .sis file
    # however, we need quicker turnaround times and work from e:\python, which is the path where python scripts are loaded from
    if g_isRealPhone:
        addAssign("PROGDIR:", "e:\python")
    else:
        addAssign("PROGDIR:", "c:\python")
else:
    import os
    addAssign("PROGDIR:", os.path.abspath(".") )

##if __name__ == "__main__":
##    print g_isPhone, g_isRealPhone
##    print "\nCurrent assigns:"
##    print g_assigns
##    filename = "PROGDir:data/g501_gps+wifi_200807021820.dict"
##    print "\nloading a testfile (dict) and display its keys:"
##    print assign(filename)
##    file = open(assign(filename))
##    s = file.read()
##    d = eval(s)
##    file.close()
##    print d.keys()
