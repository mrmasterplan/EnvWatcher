# This file defines the interface for bash-specific stuff

import sys
import re
from StringIO import StringIO

from EnvironmentObjects import EnvVariable, LocVariable, LocFunction, Alias, EWObjKey
from Debug import log



def EscapeSingleQuotes(line):
	if len(line) >2 and line[0]=="'" and line[-1]=="'":
		return line[1:-1].replace("'","'\\''")
	else:
		return line.replace("'","'\\''")

class BashEnvVariable(EnvVariable):
	"""docstring for BashEnvVariable"""
	_pattern = re.compile("""^(?P<name>[^= '"/\\\\]+?)=(?P<value>.*)\n?$""")
		
	def DefineCode(self):
		return "export %s=%s;" % (self._name,self._value)
	
	def RemoveCode(self):
		return "unset %s;\n" % self.name 
	


class BashLocVariable(LocVariable):
	"""docstring for BashLocVariable"""
	_pattern = re.compile("""^(?P<name>[^= '"/\\\\]+?)=(?P<value>.*)\n?$""")
	
	def DefineCode(self):
		return "%s=%s;" % (self._name, self._value)
	
	def RemoveCode(self):
		return "unset %s;\n" % self.name 
	


class BashLocFunction(LocFunction):
	"""docstring for BashLocFunction"""
	_pattern = re.compile("""^(?P<name>[^= ]+) \(\) \n?$""")
		
	def ParseBodyLine(self, line):
		if self.value:
			self.value += "\n"
		self.value += line
		return (line == "}") # when this is encountered, the function is closed, any loop should terminate here.
	
	def DefineCode(self):
		return "function %s %s" % (self._name, self._value)
	
	def RemoveCode(self):
		return "unset %s;\n" % self.name 
	


class BashAlias(Alias):
	"""docstring for BashAlias"""
	_pattern = re.compile("""^alias (?P<name>[^=]+)=(?P<value>.*)\n?$""")
		
	def DefineCode(self):
		return "alias %s=%s;" % (self._name, self._value)
	
	def RemoveCode(self):
		return "unalias %s\n" % self.name

		
class BashInteractor(object):
	"""Is able to read and write BASH code"""
	
	_loc_tag = "ENV_WATCHER_LOCALS>>"
	_ali_tag = "ENV_WATCHER_ALIAS>>"
	
	_ignore_file = "bash_ignore.txt"
	
	def __init__(self, conf_dir, input):
		super(BashInteractor, self).__init__()
		self.conf_dir = conf_dir
		self.ignore = self.GetIgnoreList(self.conf_dir+"/"+self._ignore_file)
		self.input = input
		self.env_dict = None
	
	@property
	def environment(self):
		if not self.env_dict:
			self.env_dict = self.ParseAll(self.input)
		return self.env_dict
	
	def GetIgnoreList(self, filename):
		ignore_file = open(filename).read().splitlines()
		ignore_list=[]
		for line in ignore_file:
			line = line.strip()
			# Take out comments
			if not line or line[0] == "#":
				continue
			ignore_list.append(line)
		
		return ignore_list
	
		
	def ParseAll(self,text):
		log("Now Parsing bash environment",text)
		env_dict = {}
		
		# first get the environment:
		import os
		for name,value in os.environ.iteritems():
			# honor the ignore configuration
			if name in self.ignore:
				continue
			obj = BashEnvVariable(name, value)
			env_dict[obj.key()] = obj
		
		# next parse the text that was passed on from the function.
		intext = iter(text.splitlines())
		for line in intext:
			if not line:
				continue
			if line == self._loc_tag:
				break
		for line in intext:
			if not line:
				continue
			if line == self._ali_tag:
				break
			# Now ready to parse local variables
			# The locals can eiter be variables or functions
			if BashLocVariable.Matches(line):
				obj = BashLocVariable.Parse(line)
			elif BashLocFunction.Matches(line):
				obj = BashLocFunction.Parse(line)
				for line in intext:
					if obj.ParseBodyLine(line):
						break
			else:
				print >>sys.stderr,"Warning: unknown bash environment line:\n\t=>"+line
				log("unknown bash environment line:\n\t=>",line)
				continue
			#Bash inserts the environment variables into the local variables.
			# I therefore want to make sure this wasn't an EnvVariable
			if obj.name in os.environ:
				continue
			
			# honor the ignore configuration
			if obj.name in self.ignore:
				continue
			
			env_dict[obj.key()] = obj
		
		for line in intext:
			if not line:
				continue
			# Now ready to parse alias
			if not BashAlias.Matches(line):
				log("Warning: unknown bash alias:\n\t=>",line)
				print >>sys.stderr,"Warning: unknown bash alias:\n\t=>"+line
				continue
			obj = BashAlias.Parse(line)
			
			# honor the ignore configuration
			if obj.name in self.ignore:
				continue
			env_dict[obj.key()] = obj
		
		# for k, v in env_dict.iteritems():
		#	 print v.DefineCode()
		return env_dict
	

