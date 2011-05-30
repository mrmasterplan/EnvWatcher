
# This file needs to be sourced. It cannot be executed.


OLDDIR=$PWD
cd $(dirname $BASH_SOURCE)
export ENV_WATCHER_DIR="$(pwd)"
cd $OLDDIR
unset OLDDIR

export ENV_WATCHER_SESSION=$(mktemp -d /tmp/EnvWatcher_session_XXXXXXXX)

function env-watcher {
    #This is done so that the tag-lines do not appear in the
    # definition of this function, which of course is itself part of
    # the environment.
    var1="ENVIRONMENT"
    var2="LOCALS"
    var3="ALIAS"
    
    eval $($ENV_WATCHER_DIR/envwatcher.py $@ <<EOF
ENV_WATCHER: ${var1}
$(env)
ENV_WATCHER: ${var2}
$(set)
ENV_WATCHER: ${var3}
$(alias)
EOF
    )
}