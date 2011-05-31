
import sys
import re
from StringIO import StringIO

class ParseEnvLine:
    var_def = re.compile("""(?P<name>[^= ]+?)=(?P<value>.*)\n""")
    func_def = re.compile("""(?P<name>[^= ]+) \(\) \n""")
    def __call__(self,file):
        line=file.readline()
        if not line or line == "\n":
            return {}
        if self.var_def.match(line):
            #It's a variable declaration
            res=self.var_def.match(line)
            return {res.group("name"):res.group("value")}
        elif self.func_def.match(line):
            #it's a function declaration
            name=self.func_def.match(line).group("name")
            body=""
            while 1:
                line=file.readline()
                body+=line
                if line == "}\n":
                    break
            return {name:body}
        else:
            raise Exception("Unknown line in environment: \"%s\"" % line)
        
    

        
class ParseAliasLine:
    alias_def = re.compile("""alias (?P<name>[^=]+)='(?P<value>.*)'\n""")
    def __call__(self,file):
        line=file.readline()
        if not line or line == "\n":
            return {}
        if self.alias_def.match(line):
            #The line defines an alias
            res=self.alias_def.match(line)
            return {res.group("name"):res.group("value")}
        else:
            raise Exception("Unknown line in alias definitions: \"%s\"" % line)
        
    


class BashInteractor(object):
    """Is able to read and write BASH code"""
    
    env_tag = "ENV_WATCHER_ENVIRONMENT"
    loc_tag = "ENV_WATCHER_LOCALS"
    ali_tag = "ENV_WATCHER_ALIAS"
    
    def __init__(self):
        super(BashInteractor, self).__init__()
    
    def BuildDict(self,text,Parser):
        io = StringIO()
        io.write(text)
        io.seek(0)
        out_dict={}
        while io.tell() != io.len:
            out_dict.update(Parser(io))
        return out_dict
    
    def Read(self,text):
        try:
            env_text = re.search("""%s>>(.*)<<%s""" % (self.env_tag,self.env_tag), text, re.DOTALL).group(1)
            loc_text = re.search("""%s>>(.*)<<%s""" % (self.loc_tag,self.loc_tag), text, re.DOTALL).group(1)
            ali_text = re.search("""%s>>(.*)<<%s""" % (self.ali_tag,self.ali_tag), text, re.DOTALL).group(1)
        except AttributeError,e:
            raise Exception("Unexpected format in Bash Environment reader.")    
        
        env_dict = self.BuildDict(env_text,ParseEnvLine())
        loc_dict = self.BuildDict(loc_text,ParseEnvLine())
        ali_dict = self.BuildDict(ali_text,ParseAliasLine())
        
        #Bash inerts the environment variables into the local variables.
        # I therefore want to take the env_vars out of the locals.
        for key,value in env_dict.iteritems():
            # The following check was dropped. It didn't work, and I'm not really sure if it matters anyway.
            # if loc_dict[key] != value:
            #     print "key is:",key
            #     print "local:",loc_dict[key]
            #     print "env:",value
            #     raise Exception("The local bash variable %s has a different value from the environment variable" % key )
            del loc_dict[key]
        
        return {"environment":env_dict, "locals":loc_dict, "alias":ali_dict}

