# This file defines the interface for bash-specific stuff

import sys
import re
from StringIO import StringIO

from EnvironmentObjects import EnvVariable, LocVariable, LocFunction, Alias, EWObjKey

def EscapeSingleQuotes(line):
    if len(line) >2 and line[0]=="'" and line[-1]=="'":
        return line[1:-1].replace("'","'\\''")
    else:
        return line.replace("'","'\\''")

class BashEnvVariable(EnvVariable):
    """docstring for BashEnvVariable"""
    _pattern = re.compile("""^(?P<name>[^= ]+?)=(?P<value>.*)\n?$""")
        
    def DefineCode(self):
        return "export %s='%s';" % (self._name, EscapeSingleQuotes(self._value))
    
    def RemoveCode(self):
        return "unset %s;\n" % self.name 
    


class BashLocVariable(LocVariable):
    """docstring for BashLocVariable"""
    _pattern = re.compile("""^(?P<name>[^= ]+?)=(?P<value>.*)\n?$""")
    
    def DefineCode(self):
        return "%s='%s';" % (self._name, EscapeSingleQuotes(self._value))
    
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
    
    _env_tag = "ENV_WATCHER_ENVIRONMENT>>"
    _loc_tag = "ENV_WATCHER_LOCALS>>"
    _ali_tag = "ENV_WATCHER_ALIAS>>"
    
    _ignore_file = "bash_ignore.txt"
    
    def __init__(self,conf_dir, input):
        super(BashInteractor, self).__init__()
        self.conf_dir = conf_dir
        self.ignore = self.GetIgnoreList(self.conf_dir+"/"+self._ignore_file)
        self.environment = self.ParseAll(input)
    
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
        intext = iter(text.splitlines())
        
        env_dict = {}
        for line in intext:
            if not line:
                continue
            if line == self._env_tag:
                break
        for line in intext:
            if not line:
                continue
            if line == self._loc_tag:
                break
            # Now ready to parse environment
            # every line here has be be of the same form
            if not BashEnvVariable.Matches(line):
                print >>sys.stderr,"Warning: unknown bash environment line:\n\t=>"+line
                continue
            obj = BashEnvVariable.Parse(line)
            if obj.name in self.ignore:
                continue
            env_dict[obj.key()] = obj
        for line in intext:
            if not line:
                continue
            if line == self._ali_tag:
                break
            # Now ready to parse local variables
            # The locals can eiter be variables or functions
            if BashLocVariable.Matches(line):
                obj = BashLocVariable.Parse(line)
                #Bash inserts the environment variables into the local variables.
                # I therefore want to make sure this wasn't already an EnvVariable
                if EWObjKey( BashEnvVariable, obj.name ) in env_dict:
                    continue
            elif BashLocFunction.Matches(line):
                obj = BashLocFunction.Parse(line)
                for line in intext:
                    if obj.ParseBodyLine(line):
                        break
            else:
                print >>sys.stderr,"Warning: unknown bash local environment line:\n\t=>"+line
                continue
            if obj.name in self.ignore:
                continue
            
            env_dict[obj.key()] = obj
        
        for line in intext:
            if not line:
                continue
            # Now ready to parse alias
            if not BashAlias.Matches(line):
                print >>sys.stderr,"Warning: unknown bash alias:\n\t=>"+line
                continue
            obj = BashAlias.Parse(line)
            if obj.name in self.ignore:
                continue
            env_dict[obj.key()] = obj
        
        # for k, v in env_dict.iteritems():
        #     print repr(v)#v.DefineCode()
        return env_dict
    

