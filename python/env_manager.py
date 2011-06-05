
import re
import os
import sys
import pickle

class env_manager(object):
    """The shell-independent manger that makes the diffs and stores the states"""
    
    tag_line = "CODE_FOLLOWS>>"
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
        
    def ConstructDifference( old, new ):
        pass
    
    def RevertDifference(env, diff):
        pass
    
    # the following defines the set of possible actions that a user can choose from.
    def record(self,name):
        self.SanityCheckName(name)
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        if os.path.exists( session_file_name ):
            print >>sys.stderr, "Warning: Open session '%s' exists. Overwriting." % name
        
        session_file = open( session_file_name, "w" )
        pickle.dump(self.shell.environment, session_file)
        session_file.close()
        
        print "Started recording session '%s'" % name
        print self.tag_line
        return 0
    
    
    def stop(self,name):
        self.SanityCheckName(name)
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        state_file_name = self.session_dir + os.sep + self.state_pattern % name
        if not os.path.exists(session_file_name):
            print >>sys.stderr, "Error: No recording session with name '%s' found."% name
            return 127
        if os.path.exists( state_file_name ):
            print >>sys.stderr, "Warning: Saved state '%s' exists. Overwriting." % name
        
        #Ok, now we have to make the diff. This is the hard part :)
        new_env = self.shell.environment
        old_env = pickle.load(open(session_file_name))
        os.remove(session_file_name) # just cleaning up as I go along
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
        
        state_file = open(state_file_name,"w")
        pickle.dump(diff,state_file)
        state_file.close()
        
        print "Saved record with name '%s'" % name
        print self.tag_line
        return 0
    
    
    def revert(self,name):
        return self.reapply(name,Reverse=True)
    
    def reapply(self,name,Reverse = False):
        self.SanityCheckName(name)
        
        import os, pickle, sys
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        state_file_name = self.session_dir + os.sep + self.state_pattern % name
        if not os.path.exists(state_file_name):
            if os.path.exists(session_file_name):
                print >>sys.stderr, "Session '%s' is still open. Please close it first."% name
            else:
                print >>sys.stderr, "Unknown session '%s'"%name
            print self.tag_line
            return 127
        
        state_file = open(state_file_name)
        state = pickle.load(state_file)
        state_file.close()
        
        env = self.shell.environment
        if not Reverse:
            print "Now applying changes recorded for session '%s':" %name
        else:
            print "Now reverting changes recorded for session '%s':" %name
        changes = ""
        for k,v in state.iteritems():
            changes += v.Apply(env,Reverse=Reverse) +"\n"
        
        print self.tag_line
        print changes
        return 0
    
    def usage(self,**kwargs):
        print open(self.main_dir+"/usage.txt").read()
        print self.tag_line
        return 0
    
    def display(self, name):
        self.SanityCheckName(name)
        # check if we have a state or a record with this name:
        import os, pickle, sys
        session_file_name = self.session_dir + os.sep + self.session_pattern % name
        state_file_name = self.session_dir + os.sep + self.state_pattern % name
        if os.path.exists(session_file_name):
            session = pickle.load(open(session_file_name))
            print "Now displaying definitions in session '%s':" %name
            for k,v in session.iteritems():
                v.PrintDefinition()
        elif os.path.exists(state_file_name):
            state = pickle.load(open(state_file_name))
            print "Now displaying changes recorded for session '%s':" %name
            for k,v in state.iteritems():
                print repr(v)
        else:
            print >>sys.stderr, "No known records with name '%s'" % name
        print self.tag_line
        return 0
    
    actions = [record, stop, revert, reapply, usage, display ]
    action_names = { a.func_name:a for a in actions }