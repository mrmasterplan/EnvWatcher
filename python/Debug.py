
import time
import inspect
import sys
import traceback

class Logger(object):
    """docstring for MyLogger"""
    def __init__(self, filename):
        super(Logger, self).__init__()
        self.logfile = open(filename,"a")
        # self.logfile = sys.stdout
    
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
Env_dir = os.environ["ENV_WATCHER_DIR"]
log_file_name="Log_"+time.strftime("%Y_%m_%d")+".txt"

if "-d" in sys.argv or "--debug" in sys.argv:
    log = Logger(Env_dir+os.sep+log_file_name)
else:
    log = DummyLogger


