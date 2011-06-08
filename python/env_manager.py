"""The manager module that hadles the user input"""

# On naming conventions in this code...
#
# A "Session" is an open recording where the difference to the 'after' snapshot has not yet been taken.
# It is a dictionary that maps EnvironmentObjects.EnvObjKey objects to the shell specific variable objects,
# for example it maps a EnvObjKey(BashEnvVariable,"PATH") to BashEnvVariable("PATH","/bin:/usr/local/bin")
# A session is stored in the session files.
#
# A "State" is a difference object. It is a dictionary of EnvObjKeys to EnvironmentObjects.EWDiffObjects
# the keys refer to the variables that are affected. The EWDiffObjects contiain the difference between the
# before and the after state.


import re
import os
import sys
import pickle

from Debug import log

# This is that tag-line that the shell-function looks for.
# output after it will be evaluated as code in the shell.
tag_line = "CODE_FOLLOWS>>"

class env_manager(object):
	"""The shell-independent manger that makes the diffs and stores the states"""
	
	session_pattern = "session_%s_.log"
	state_pattern = "state_%s_.log"
	
	def __init__(self, shell, session_dir, main_dir):
		super(env_manager, self).__init__()
		self.shell = shell
		import os
		self.session_dir = os.path.normpath(session_dir)+os.sep
		self.main_dir = os.path.normpath(main_dir)+os.sep
		log("initialized the EnvManager")
	
	# Exceptions:
	# ===========
	# I want to define the excections centally here so that they are easier to keep track of
	
	class UnknownState(Exception):
		def __init__(self,name):
			Exception.__init__(self, "No record with name '%s' found."% name)
	
	class UnknownSession(Exception):
		def __init__(self,name):
			Exception.__init__(self, "No recording session with name '%s' found."% name)
	
	class UnknownName(Exception):
		def __init__(self,name):
			Exception.__init__(self, "No record or recording session with name '%s' found."% name)
	
	class NameError(Exception):
		def __init__(self,name):
			Exception.__init__(self,"Invalid name '%s'. Letters, numbers and underscores only, please."%name)
	
	class WriteError(Exception):
		def __init__(self,name):
			Exception.__init__(self,"Unable to write to file %s"%name)
	
	class SessionExists(Exception):
		def __init__(self,name):
			Exception.__init__(self,"Session %s exists."%name)
	
	class StateExists(Exception):
		def __init__(self,name):
			Exception.__init__(self,"Session %s exists."%name)
	
	# Session and State accesss methods.
	# If you want to change where sessions and states are saved, look here
	def SanityCheckName(self,name):
		"""The way to check that the name is good.
		For now we only allow letters, numbers and underscores.
		The name is used directly as part of a file-name and should therefore be nice."""
		import re
		if not re.match("""[a-zA-Z0-9_]+""", name):
			raise self.NameError(name)
	
	
	def SessionDir(self):
		return self.session_dir
	
	
	def SessionName(self,name, nocheck=False):
		"""The only way anyone whould ever contruct the session name"""
		if not nocheck:
			self.SanityCheckName(name)
		return self.session_dir + os.sep + self.session_pattern % name
	
	
	def StateName(self,name, nocheck=False):
		"""The only way anyone should ever construct the state name"""
		if not nocheck:
			self.SanityCheckName(name)
		return self.session_dir + os.sep + self.state_pattern % name
	
	
	def ClearSession(self,name, verbose=True):
		import os
		if os.path.exists(self.SessionName(name)):
			if verbose:
				print >>sys.stderr, "Warning: Open session %s exists. Overwriting."%name
			log("removing session %s"%name)
			os.remove(self.SessionName(name))
	
	
	def ClearState(self,name,verbose=True):
		import os
		if os.path.exists(self.StateName(name)):
			if verbose:
				print >>sys.stderr, "Warning: Saved state %s exists. Overwriting."%name
			log("removing state %s"%name)
			os.remove(self.StateName(name))
	
	
	def UserClearSession(self,name):
		import os,sys,re
		if os.path.exists(self.SessionName(name)):
			force = ("-f" in sys.argv or "--force" in sys.argv)
			if not force:
				print >>sys.stderr, "Open session %s exists. Do you want to overwrite? "  % name,
				user=raw_input()
				log("Question:","Open session %s exists. Do you want to overwrite? "  % name,"answer:",user)
				if re.match("""y(es?)?""",user):
					print >>sys.stderr," --> Overwriting."
					return self.ClearSession(name,False)
				else:
					raise self.SessionExists(name)
			else:
				self.ClearSession(name)
	
	
	def UserClearState(self,name):
		import os,sys,re
		if os.path.exists(self.StateName(name)):
			force = ("-f" in sys.argv or "--force" in sys.argv)
			if not force:
				print >>sys.stderr, "Saved state %s exists. Do you want to overwrite? "  % name,
				user=raw_input()
				log("Question:","Saved state %s exists. Do you want to overwrite? "  % name,"answer:",user)
				if re.match("""y(es?)?""",user):
					print >>sys.stderr," --> Overwriting."
					return self.ClearState(name,False)
				else:
					raise self.StateExists(name)
			else:
				self.ClearState(name)
	
	
	# The file access methods.
	# if you want to change the way that the sessions and states are serialized and deserialized, look here.
	def GetState(self, name):
		import os
		log("Session Dir",os.listdir(self.session_dir))
		try:
			import pickle
			return pickle.load(open(self.StateName(name)))
		except:
			log()
			log("raising unknown state now.")
			raise self.UnknownState(name)
	
	
	def GetSession(self,name):
		import os
		log("Session Dir",os.listdir(self.session_dir))
		try:
			import pickle
			return pickle.load(open(self.SessionName(name)))
		except:
			log()
			log("raising unknown session now.")
			raise self.UnknownSession(name)
	
	
	def WriteState(self,name,state):
		state_name = self.StateName(name)
		import os, sys, pickle
		if os.path.exists(state_name):
			print >>sys.stderr, "Warning: Recording '%s' exists. Overwriting." % name
			log("overwriting state %s"%name,state_name)
		try:
			state_file = open(state_name,"w")
			pickle.dump(state,state_file)
			state_file.close()
		except:
			log()
			raise self.WriteError(state_name)
		log("written",state_name)
	
	def WriteSession(self,name,session):
		session_name = self.SessionName(name)
		import os, sys, pickle
		if os.path.exists(session_name):
			print >>sys.stderr, "Warning: Open session '%s' exists. Overwriting." % name
			log("overwriting session %s"%name,session_name)
		try:
			session_file = open(session_name,"w")
			pickle.dump(session,session_file)
			session_file.close()
		except:
			log()
			raise self.WriteError(session_name)
		log("written",session_name)
	
	# The methods concerned with the before-after differences.
	def ConstructDifference(self, old_env, new_env ):
		"""Construct the dictionary of EWDiffObjects that is called a 'state'."""
		from EnvironmentObjects import EWDiffObject
		diff = {}
		#consider all keys that are in either einvironment, old or new
		for key in set(new_env.keys() + old_env.keys()):
			if key not in new_env:
				#it must be in old_env
				diff[key] = EWDiffObject(old=old_env[key])
				# new is none, this corresponds to a removal
			elif key not in old_env:
				# it must be in new_env
				diff[key] = EWDiffObject(new=new_env[key])
				# old is none, this is an addition
			else:
				# maybe nothing changed? This is most likely.
				if old_env[key] != new_env[key]:
					# something changed
					diff[key] = EWDiffObject(old=old_env[key], new=new_env[key])
		return diff
	
	
	def GetStateOrSessionDiff(self,name):
		import os
		log("Session Dir",os.listdir(self.session_dir))
		"""If an existing saved state by this name is found, return that,if an open session by this name is found, construct the difference to the present."""
		session_file_name = self.SessionName(name)
		state_file_name = self.StateName(name)
		try:
			diff = self.GetState(name)
		except:
			log()
			log("session wans't available. making it.")
			diff = None
		if not diff:
			try:
				diff = self.ConstructDifference(self.GetSession(name), self.shell.environment)
			except:
				log()
				log("that didn't work either")
				raise self.UnknownName(name)
		return diff
	
	
	# The stuff that the actions do without all the unser interaction:
	def CloseSession(self,name):
		"""Close an existing open recording session"""
		oldsession = self.GetSession(name)
		diff = self.ConstructDifference(oldsession, self.shell.environment)
		self.WriteState(name, diff)
		
		# Remove the session file, thereby closing the session
		import os
		os.remove(self.SessionName(name))
	
	
	# the following defines the set of possible actions that a user can choose from.
	# the user options are created from the list that follows these functions.
	
	def start(self,name):
		"""start a new recording session"""
		session_file_name = self.SessionName(name)
		state_file_name = self.StateName(name)
		import os
		
		self.UserClearSession(name)
		self.UserClearState(name)
		
		self.WriteSession(name,self.shell.environment)
		
		print "Started recording session '%s'" % name
		print tag_line
		return 0
	
	
	def stop(self,name):
		"""Close an open recording session"""
		import os
		if os.path.exists(self.SessionName(name)):
			self.UserClearState(name)
		self.CloseSession(name)
		print "Saved record with name '%s'" % name
		print tag_line
		return 0
	
	
	def undo(self,name):
		"""remove the changes associated with a state."""
		import os
		if not os.path.exists(self.StateName(name)) and os.path.exists(self.SessionName(name)):
			force = ("-f" in sys.argv or "--force" in sys.argv)
			if force:
				self.ClearState(name)
				self.CloseSession(name)
			else:
				print >>sys.stderr, "Session %s is open. Do you want to close it? "  % name,
				user=raw_input()
				log("Question:","Session %s is open. Do you want to close it? "  % name,"answer:",user)
				if re.match("""y(es?)?""",user):
					print >>sys.stderr," --> Closing."
					self.UserClearState(name)
					self.CloseSession(name)
				else:
					print >>sys.stderr," --> Using open session."
		
		return self.redo(name,Reverse=True) 
	
	
	def redo(self,name,Reverse = False):
		state = self.GetStateOrSessionDiff(name)
		
		env = self.shell.environment
		if not Reverse:
			print "Now applying changes recorded for session '%s'" %name
		else:
			print "Now reverting changes recorded for session '%s'" %name
		changes = ""
		for k,v in state.iteritems():
			changes += v.Apply(env,Reverse=Reverse) +"\n"
		
		print tag_line
		print changes
		return 0
	
	
	def usage(self,**kwargs):
		print open(self.main_dir+"/usage.txt").read()
		print tag_line
		return 0
	
	
	def display(self, name):
		state = self.GetStateOrSessionDiff(name)
		for k,v in state.iteritems():
			print v.Display()
		print tag_line
		return 0
	
	
	def list(self,**kwargs):
		import os, glob, re
		log("Session Dir",os.listdir(self.session_dir))
		
		session_files = glob.glob(self.SessionName("*",nocheck=True))
		session_match = re.compile(os.sep+os.path.basename(self.SessionName("(?P<name>.*?)",nocheck=True))+"$")
		
		if session_files:
			print "Open sessions:"
			for name in session_files:
				print "\t%s"%session_match.search(name).group("name")
		else:
			print "No open sessions."
		
		state_files = glob.glob(self.StateName("*",nocheck=True))
		state_match = re.compile(os.sep+os.path.basename(self.StateName("(?P<name>.*)",nocheck=True))+"$")
		if state_files:
			print "Avaliable records:"
			for name in state_files:
				print "\t%s"%state_match.search(name).group("name")
		else:
			print "No saved records."
		print tag_line
		return 0
	
		
	actions = [ usage, start, stop, undo, redo, display, list ]
	action_names = dict( [ (a.func_name,a) for a in actions ] )
	

