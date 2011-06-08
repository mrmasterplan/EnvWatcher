
import time
import inspect
import sys,os
import traceback

class Logger(object):
    """docstring for MyLogger"""
    def __init__(self, filename, *altfiles):
        super(Logger, self).__init__()
        altfiles = list(altfiles)
        altfiles.insert(0,filename)
        for name in altfiles:
            try:
                name = os.path.expandvars(os.path.expanduser(name))
                dir = os.path.dirname(name)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                self.logfile = open(name,"a")
                print "Writing log to",name
                break
            except:
                pass
        else:
            print >>sys.stderr,"Unable to open any of there files for logging:", self.altfiles
    
    def __call__(self, *args, **kwargs):
        caller = traceback.extract_stack()[-2]
        if not args or kwargs:
            trace = traceback.format_exc()
            if not trace:
                return
            else:
                args=[trace]
        
        print >>self.logfile, time.asctime()
        print >>self.logfile, "Log message from file "+caller[0]+" at line "+str(caller[1])+":"
        for item in args:
            print >>self.logfile, item
        for key, value in kwargs.iteritems():
            print >>self.logfile, key+":", value
        print >>self.logfile, ""
        self.logfile.flush()
        os.fsync(self.logfile)

def DummyLogger(*args,**kwargs):
    pass

import os,sys
log_file_name="Log_"+time.strftime("%Y_%m_%d")+".txt"

if "-d" in sys.argv or "--debug" in sys.argv:
    log = Logger("$ENV_WATCHER_DIR/"+log_file_name, "$HOME/.envwatcher/"+log_file_name, "$HOME/EnvWatcher_"+log_file_name)
else:
    log = DummyLogger


