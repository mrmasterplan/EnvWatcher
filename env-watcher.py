#!/usr/bin/env python

import os
import sys

session_directory=os.environ["ENV_WATCHER_SESSION"]

all_input = sys.stdin.read()

f=open(session_directory+os.sep+"hello_world.txt","w")
f.write(all_input)
f.close()
print "echo All Done;"
