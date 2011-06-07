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
  - Send me the log-files that are located in $ENV_WATCHER_DIR/Log_*.txt
    (They only get written in debug mode.)
Please send all of the above information to EnvWatcher@gmail.com
Thank you. I will hopefully get back to you soon.

LICENCE
=======

Copyright (C) 2011 Simon Heisterkamp and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.