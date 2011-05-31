
import re
import os
import sys
import pickle

class env_manager(object):
    """The shell-independent manger that makes the diffs and stores the states"""
    
    tag_line = "ENVIRONMENT_FOLLOWS"
    session_pattern = "session_%s_.log"
    state_pattern = "state_%s_.log"
    
    def __init__(self, shell, session_dir, main_dir):
        super(env_manager, self).__init__()
        self.shell = shell
        self.session_dir = session_dir
        self.main_dir = main_dir
        
    
    def SanityCheckName(self,name):
        if not re.match("""[a-zA-Z0-9_]+""", name):
            raise Exception("Invalid name. Letters, numbers and underscores only.")
        
    
    def ReadInput(self,text):
        self.in_env=self.shell.Read(text)
        
    
    def SmartDictDiff( old, new ):
        pass
        
    
    # the following defines the set of possible actions that a user can choose from.
    def record(self,name):
        self.SanityCheckName(name)
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        if os.path.exists( session_file_name ):
            print >>sys.stderr, "Warning: Open session '%s' exists. Overwriting." % name
        
        session_file = open( session_file_name, "w" )
        pickle.dump(self.in_env, session_file)
        session_file.close()
        
        print "Started recording session '%s'" % name
        
    
    def stop(self,name):
        self.SanityCheckName(name)
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        state_file_name = self.session_dir + os.sep + self.state_pattern % name
        if not os.path.exits(session_file_name):
            print >>sys.stderr, "Error: No recording session with name '%s' found."%s
            return 127
        if os.path.exists( state_file_name ):
            print >>sys.stderr, "Warning: Saved state '%s' exists. Overwriting." % name
        
        #Ok, now we have to make the diff. This is the hard part :)
        new_env = self.in_env
        old_env = pickle.load(open(session_file_name))
        os.remove(session_file_name) # just cleaning up as I go along
        
        
        
    def revert(self,name):
        self.SanityCheckName(name)
        pass
        
    def usage(self,**kwargs):
        print open(self.main_dir+"/usage.txt").read()
        return 0
        
    actions = [ record, stop, revert, usage ]
    action_names = { a.func_name:a for a in actions }