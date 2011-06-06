
import re
import os
import sys
import pickle

tag_line = "CODE_FOLLOWS>>"

class env_manager(object):
    """The shell-independent manger that makes the diffs and stores the states"""
    
    session_pattern = "session_%s_.log"
    session_match = "/session_(?P<name>.*)_.log$"
    state_pattern = "state_%s_.log"
    state_match = "/state_(?P<name>.*)_.log$"
    
    def __init__(self, shell, session_dir, main_dir):
        super(env_manager, self).__init__()
        self.shell = shell
        self.session_dir = session_dir
        self.main_dir = main_dir
        
    
    def SanityCheckName(self,name):
        if not re.match("""[a-zA-Z0-9_]+""", name):
            raise Exception("Invalid name. Letters, numbers and underscores only.")
    
    def GetDiff(self,name):
        self.SanityCheckName(name)
        import os, pickle, sys
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        state_file_name = self.session_dir + os.sep + self.state_pattern % name
        
        if os.path.exists(state_file_name):
            state_file = open(state_file_name)
            state = pickle.load(state_file)
            state_file.close()
        elif os.path.exists(session_file_name):
            old_env = pickle.load(open(session_file_name))
            state = self.ConstructDifference(old_env,self.shell.environment)
        else:
            raise Exception("Unknown recording '%s'"%name )
        return state
    
    def ConstructDifference(self, old_env, new_env ):
        from EnvironmentObjects import EWDiffObject
        diff = {}
        keys = set(new_env.keys() + old_env.keys())
        for key in keys:
            if key not in new_env:
                diff[key] = EWDiffObject(old=old_env[key])
            elif key not in old_env:
                diff[key] = EWDiffObject(new=new_env[key])
            else:
                if old_env[key] != new_env[key]:
                    diff[key] = EWDiffObject(old=old_env[key], new=new_env[key])
        return diff
    
    # the following defines the set of possible actions that a user can choose from.
    def start(self,name):
        import os
        self.SanityCheckName(name)
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        state_file_name = self.session_dir + os.sep + self.state_pattern % name
        
        if os.path.exists( session_file_name ):
            print >>sys.stderr, "Warning: Open session '%s' exists. Overwriting." % name
        if os.path.exists( state_file_name ):
            print >>sys.stderr, "Warning: Saved state '%s' exists. Removing." % name
            import os
            os.remove(state_file_name)
        
        session_file = open( session_file_name, "w" )
        pickle.dump(self.shell.environment, session_file)
        session_file.close()
        
        print "Started recording session '%s'" % name
        print tag_line
        return 0
    
    
    def stop(self,name):
        self.SanityCheckName(name)
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        state_file_name = self.session_dir + os.sep + self.state_pattern % name
        if not os.path.exists(session_file_name):
            raise Exception("No recording session with name '%s' found."% name)
        if os.path.exists( state_file_name ):
            print >>sys.stderr, "Warning: Saved state '%s' exists. Overwriting." % name
        
        #Ok, now we have to make the diff. This is the hard part :)
        old_env = pickle.load(open(session_file_name))
        os.remove(session_file_name) # just cleaning up as I go along
        
        diff = self.ConstructDifference(old_env,self.shell.environment)
        
        state_file = open(state_file_name,"w")
        pickle.dump(diff,state_file)
        state_file.close()
        
        print "Saved record with name '%s'" % name
        print tag_line
        return 0
    
    
    def undo(self,name):
        return self.redo(name,Reverse=True)
    
    def redo(self,name,Reverse = False):
        
        state = self.GetDiff(name)
        
        env = self.shell.environment
        if not Reverse:
            print "Now applying changes recorded for session '%s':" %name
        else:
            print "Now reverting changes recorded for session '%s':" %name
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
        self.SanityCheckName(name)
        # check if we have a state or a record with this name:
        state = self.GetDiff(name)
        for k,v in state.iteritems():
            print v.Display()
        print tag_line
        return 0
    
    def list(self,**kwargs):
        session_file_name = self.session_dir + os.sep + self.session_pattern % "*"
        state_file_name = self.session_dir + os.sep + self.state_pattern % "*"
        import glob
        session_files = glob.glob(session_file_name)
        state_files = glob.glob(state_file_name)
        print "Open sessions:"
        if session_files:
            for name in session_files:
                print "\t%s"%re.search(self.session_match,name).group("name")
        else:
            print "\tNo open sessions."
        print "Avaliable records:"
        if state_files:
            for name in state_files:
                print "\t%s"%re.search(self.state_match,name).group("name")
        else:
            print "\tNo records avaliable."
        print tag_line
        return 0
    
        
    actions = [ usage, start, stop, undo, redo, list, display ]
    action_names = dict( [ (a.func_name,a) for a in actions ] )