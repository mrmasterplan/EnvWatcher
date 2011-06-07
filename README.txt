This is EnvWatcher.
===================
A project by Simon Heisterkamp.
  Please send comments/suggestions/bugs to EnvWatcher@gmail.com)
  ( Please also read the section below on reporting bugs. )

Requirements
============
    - bash
    - python
        Tested for python 2 version 2.4 and up.

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

In its functionality the env-watcher is not unlike other dynamic environment loaders
like, for example, 'module' (http://modules.sourceforge.net/). However, module requires
the user to write special tcl modules in order to be able to load and unload them. The
advantage of env-watcher is that it can accept and recognize changes made by any other
shell-script because it relies on 'before' and 'after' snapshots of the shell
environment.

The env-watcher monitors
    - environment variables
    - local variables
    - shell functions
    - aliases

BUGS
====

In the unlikely event that you encounter any bugs *ahem* please do the following:
  - Repeat the steps that lead you to the bug using debug-mode in each step.
    Debug mode is enabled by including the -d option on the command line.
  - Send me the entire output of your session.
  - Send me the log-file that is located in $ENV_WATCHER_DIR/log.tmp
    (Only gets written in debug mode.)
Please send all of the above information to EnvWatcher@gmail.com
Thank you. I will hopefully get back to you soon.