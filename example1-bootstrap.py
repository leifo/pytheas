# Pytheas example 1 - bootstrap
# Leif Oppermann, 25.09.2009

'''
This example shows how to use the bootstrapping code, which acts as a mediator for platform differences.

In particular, this example code shows three things:
1) how to make use of the supplied code (use the template below)
2) how to use the variables to know what you are running on
3) how to load a file from a subdirectory of the current directory, even on Symbian OS which
   does not have current directory, by making use of the "PROGDIR:" assign which is installed by the template
'''


#---lesson 1, use this template

#---take the following code to automatically distinguish between real phone, phone emulator or desktop
#   and set Python import paths accordingly. also sets "PROGDIR:" assign to where the code is running from
#   (see modules/assigns.py for more details)
#BEGIN
try:
    # for platforms that have a notion of current directory
    execfile("lxo_bootstrap.py")
except:
    # for series 60, which doesn't have a current directory
    try:
        execfile("e:\\python\\lxo_bootstrap.py")
    except:
        try:
            execfile("c:\\python\\lxo_bootstrap.py")
        except:
            g_isPhone=False
            print "***Error: lxo_bootstrap.py not found"
#END

#---lesson2, know what you are running on
if g_isPhone:
    print "Running on Python S60"
    if g_isRealPhone:
        print "(on actual hardware)"
    else:
        print "(in an emulator)"
else:
    print "Running on other flavour of Python, probably on a desktop"


#---lesson3, load a file with the supplied mechanism
filename="PROGDIR:idata/example1_dat.txt"
fullfilename = assign(filename)
print "Loading '%s' (from '%s')..." %(filename, fullfilename)
s = open(fullfilename).read()
print "Contents of file:\n'''"
print s
print "'''\nEnd of example 1"