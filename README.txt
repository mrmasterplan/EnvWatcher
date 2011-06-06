This is EnvWatcher.
===================
A project by Simon Heisterkamp (heisterkamp@nbi.dk)

SETUP
=====
Simply source the script setup.sh

    $ source path/to/EnvWatcher/setup.sh

You will now have access to the command env-watcher.
Full usage information can be found in the file usage.txt or by calling 

    $ env-watcher usage

Description
===========

env-watcher is able to monitor your bash environment and record changes that you make to
it. One can then ask the env-watcher to undo those changes.

In its functionallity the env-watcher is not unlike other dynamic environment loaders
like, for example, 'module' (http://modules.sourceforge.net/). However, module requires
the user to write special tcl modules in order to be able to load and unload them. The
advantage of env-wrapper is that it can accept and recognize changes made by any other
shell-script because it relies on 'before' and 'after' snapshots of the shell
environment.

env-watcher monitors
    - environment variables
    - local variables
    - shell functions
    - aliases

