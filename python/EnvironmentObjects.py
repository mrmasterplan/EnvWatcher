"""This mudule defines those properties of Envionmnet objects which I believe to be common to all
shells."""


class EWObjKey(object):
    """Serve as an access key to the Environmen Object.
    A EWObjKey encodes the name of the object as well as the type.
    Type here means environemnt variable, local variable, local function or alias.
    """
    def __init__(self, item, name=""):
        """The item has to has an attribute called name."""
        super(EWObjKey, self).__init__()
        if type(item)==type:
            classtype = item
            assert( type(name) == str )
        else:
            # I was passed an intance
            classtype = item.__class__
            name = item.name
        
        typename = classtype.__name__
        
        self._class = classtype
        self._name = name
        self._typename = typename
        self._hash = hash(typename+" "+name)
    
    def MakeObject(self,value=""):
        return self._class(name=self._name,value=value)
    
    @property
    def name(self):
        return self._name
    
    def getclass(self):
        return self._class
    
    @property
    def typename(self):
        return self._typename
    
    def __hash__(self):
        return self._hash
    
    def __eq__(self,other):
        return hash(self) == hash(other)
    
    def __ne__(self,other):
        return hash(self) != hash(other)
    
    def __cmp__(self,other):
        return hash(self).__cmp__( hash(other) )
    
    def __repr__(self):
        return "<%s \"%s\">" % (self._typename,self._name)
    
    def __str__(self):
        return "<%s \"%s\">" % (self._typename,self._name)
    


class EWObject(object):
    """docstring for EWObject"""
    
    @classmethod
    def Matches(cls, defstring):
        return bool(cls._pattern.match(defstring))
    
    def __init__(self, name, value=""):
        super(EWObject, self).__init__()
        self._name = name
        self._value = value
    
    
    @classmethod
    def Parse(cls, line):
        assert(cls.Matches(line))
        res = cls._pattern.match(line).groupdict("")
        return cls(**res)
    
    
    def key(self):
        return EWObjKey(self)
    
    def _get_value(self):
        return self._value
    
    def _set_value(self, val):
        assert(type(val)==str)
        self._value = val
    
    value = property(_get_value, _set_value)
    
    @property
    def name(self):
        return self._name
    
    def __eq__(self,other):
        return self.key() == other.key() and self.value == other.value
    
    def __ne__(self,other):
        return self.key() != other.key() or self.value != other.value
    
    def __repr__(self):
        return self.__class__.__name__+"(\"%s\", \"\"\"%s\"\"\")" % (self._name, self._value.replace("\\","\\\\"))
        # return self.__class__.__name__+"(\"%s\", \"\"\"%s\"\"\")" % (self._name, self._value)


class EWVariableObject(EWObject):
    """docstring for EWVariableObject"""
    
    def __str__(self):
        return "%s='%s'" %(self._name, self._value)
    
    def IsPathVariable(self):
        # determine if this is a path variable where we should be able to do the path magic.
        import re
        pat = re.compile("path", re.IGNORECASE)
        pathlikename = bool(pat.search(self._name))
        
        import os
        # find out if any of the paths in value exist if value is of the form: path1:path2:path
        #valexists = reduce(lambda x,y: x or os.path.exists(y), self.value.split(":"), False)
        valexists = any( [ os.path.exists(path) for path in self.value.split(":") ] )
        
        # this is my best shot at guessing if this should be a path-like variable.
        return pathlikename or valexists
    


class EnvVariable(EWVariableObject):
    """An environment variable"""
    pass


class LocVariable(EWVariableObject):
    """A local shell variable"""
    pass


class LocFunction(EWObject):
    """docstring for LocFunction"""
    
    def __str__(self):
        return "%s () \n%s" %(self._name,self._value)
    


class Alias(EWVariableObject):
    """docstring for Alias"""
    pass


class EWDiffObject(object):
    """Contains the difference between two Environment Objects."""
    def __init__(self, old=None, new=None):
        if not old and not new:
            raise Exception("Nothing to initialize from")
        # get the key:
        if old:
            self._key = old.key()
        else:
            self._key = new.key()
        
        # now find out what kind of difference we need to make
        if not self.DoPathDiff(old,new):
            self.old = old
            self.new = new
            self.pathdiff = False
    
    def key(self):
        return self._key
    
    def DoPathDiff(self, old, new):
        # Find out if we can do this.
        if not ( ( isinstance(old,EWVariableObject) and old.IsPathVariable() )
                    or ( isinstance(new,EWVariableObject) and new.IsPathVariable() ) ):
            return False
        
        # We now expect this to be path-like.
        
        # determine which paths were added, and which removed.
        try:
            oldpaths = old.value.split(":")
        except:
            oldpaths = []
        
        try:
            newpaths = new.value.split(":")
        except:
            newpaths = []
        
        while "" in oldpaths:
            del oldpaths[oldpaths.index("")]
        while "" in newpaths:
            del newpaths[newpaths.index("")]
        
        oldset = set(oldpaths)
        newset = set(newpaths)
        
        self.added = list(newset - oldset)
        self.removed = list(oldset - newset)
        
        # for those paths that are in both environments,
        # find out if any have swapped place:
        oldcommonpaths = [ path for path in oldpaths if path in newpaths]
        newcommonpaths = [ path for path in newpaths if path in oldpaths]
        # the two lists now must have the same length:
        assert( len(oldcommonpaths) == len(newcommonpaths))
        indices = [ oldcommonpaths.index(path) for path in newcommonpaths ]
        # if the paths were ordered identically, the list 'indices' should be equal to range(len(indices))
        if indices == range(len(indices)):
            inversions=[]
        else:
            # the plan is now to find the set of pair inversion that are necessary to convert
            # oldcommonpaths to newcommonpaths.
            # I choose pair-inversions because they can be applied quite independently of presence
            # of other items in a list.
            tmplist = indices
            ind_inversions=[]
            while tmplist != range(len(tmplist)):
                for it in tmplist:
                    if it != tmplist.index(it):
                        break
                # we now have an it that is not at the right place:
                inv = (it,tmplist[it])
                ind_inversions.append(inv)
                # apply the swap between the two items named by inv
                self.ApplySwap(inv,tmplist)
            ind_inversions.reverse()
            inversions=[ (oldcommonpaths[inv[0]], oldcommonpaths[inv[1]]) for inv in ind_inversions ]
        
        self.inversions = inversions
        self.pathdiff = True
        return True
    
    def ApplySwap(self,inv,li):
        if inv[0] not in li or inv[1] not in li:
            return
        ind1 = li.index(inv[0])
        ind2 = li.index(inv[1])
        li[ind1],li[ind2] = li[ind2],li[ind1]
    
    def __repr__(self):
        out = repr(self.key())
        if self.pathdiff:
            out+=" {\n"
            out+="\t     added: "+repr(self.added)+"\n"
            out+="\t   removed: "+repr(self.removed)+"\n"
            out+="\tinversions: "+repr(self.inversions)+"\n}"
        else:
            out+=" { '%s' => '%s' }" %(repr(self.old),repr(self.new))
        return out
    
    def Display(self):
        out = self.key()._typename+'("%s"):' % self.key().name
        # out = repr(self.key())
        if self.pathdiff:
            out+="\n{ "
            if self.added:
                out+="\n     added: "+":".join(self.added)
            if self.removed:
                out+="\n   removed: "+":".join(self.removed)
            if self.inversions:
                out+="\ninversions: "+repr(self.inversions)
            out+="\n}"
        else:
            if self.old:
                oldval = "'%s'" % self.old.value
            else:
                oldval = "n/a"
            if self.new:
                newval = "'%s'" % self.new.value
            else:
                newval = "n/a"
            
            out+=" { %s => %s }" %(oldval,newval)
        return out
    
    
    def Apply(self, env, Reverse =False):
        #Get the object ready
        if self.key() in env:
            present_var = env[self.key()]
        else:
            present_var = None
        
        #take care of the reversal if necessary
        if Reverse:
            if self.pathdiff:
                self.added, self.removed = self.removed, self.added
                self.inversions.reverse()
            else:
                self.new = self.old
        
        if self.pathdiff:
            #If there is nothing to add, we can only remove and invert, and this needs an existing onject
            need_exisitng = not self.added
        else:
            # if the new one is none, then we want the object to go away. If it doesn't even exist, exit.
            need_exisitng = not self.new
        if need_exisitng and not present_var:
            return ""
        
        if not self.pathdiff:
            # if it's a simple matter of object addition and removal:
            if self.new:
                return self.new.DefineCode()
            else:
                return present_var.RemoveCode()
        else:
            # we need to apply the path difference
            if present_var:
                pathlist = present_var.value.split(":")
            else:
                pathlist = []
            
            
            for path in self.removed:
                if path in pathlist:
                    del pathlist[pathlist.index(path)]
            
            pathlist = self.added+pathlist
            
            for inv in self.inversions:
                self.ApplySwap(inv,pathlist)
            
            value = ":".join(pathlist)
            
            if pathlist:
                if present_var:
                    present_var.value = value
                else:
                    present_var = self.key().MakeObject(value)
                return present_var.DefineCode()
            else:
                if present_var:
                    return present_var.RemoveCode()
                else:
                    # there was none and there shall be none
                    return ""
    

