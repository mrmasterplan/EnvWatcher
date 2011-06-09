#!/usr/bin/env python
# 
# This script has the auto-completion functionality of env-watcher.
# 
# It is called from the shell when one presses TAP on a line that starts with env-watcher
#
# The intention is to first complete the possible actions. If an action has been selected,
# the available sessions and states are autocompleted.

import os
import sys
# some setup paths:
session_directory = os.environ["ENV_WATCHER_SESSION"]
main_directory = os.environ["ENV_WATCHER_DIR"]

if not session_directory or not main_directory:
	print >>sys.stderr, "Your EnvWatcher environment was not properly set up. Please use the included setup.sh file."
	sys.exit(127)

# if this fails then there is nothing I can do:
sys.path.append(os.environ["ENV_WATCHER_DIR"]+os.sep+"python")

def main():
		
	from env_manager import env_manager
	
	arguments = sys.argv
	action_names = env_manager.action_names.keys()
	
	if sys.argv[-1] in action_names:
		# we may need to autocomplete a session name
		import inspect
		if "name" in inspect.getargspec(env_manager.action_names[sys.argv[-1]])[0]:
			#The action takes the "name" argument:
			manager = env_manager(shell=None, session_dir=session_directory, main_dir=main_directory)
			sessions,states = manager.GetAllNames()
			return auto_complete(sys.argv[-2], states+sessions)
		else:
			# There is nothing to autocomplete.
			return
	else:
		# we need to auto_complete an action
		return auto_complete(sys.argv[-2], action_names)


def auto_complete(inval, words):
	possibles = []
	for word in words:
		if word.find(inval) == 0:
			possibles.append(word)
	
	if not possibles:
		return
	
	if len(possibles)==1:
		print possibles[0]+" "
		return
	
	import os.path
	lcp = os.path.commonprefix(possibles)
	if lcp==inval:
		for word in possibles:
			print word
	else:
		print lcp
	
if __name__ == '__main__':
	main()
	# res=127
	# try:
	# 	res=main()
	# except SystemExit:
	# 	log()
	# except Exception, e:
	# 	print >>sys.stderr, "ERROR:",e
	# 	log()
	# except KeyboardInterrupt:
	# 	log()
	# except:
	# 	import sys
	# 	print >>sys.stderr, "Unknown error:",sys.exc_value,sys.exc_type
	# 	log()
	# sys.exit(res)
