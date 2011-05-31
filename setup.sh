#
# This is setup.sh, the setup script of EnvWathcer for the Bourne Again SHell
# This file needs to be sourced. It cannot be executed.


OLDDIR=$PWD
cd $(dirname $BASH_SOURCE)
export ENV_WATCHER_DIR="$(pwd)"
cd $OLDDIR
unset OLDDIR

export ENV_WATCHER_SESSION=$(python -c "import tempfile; print tempfile.mkdtemp(prefix='EnvWatcher_session_')")

function env-watcher {
    local env_tag="ENV_WATCHER_ENVIRONMENT"
    local loc_tag="ENV_WATCHER_LOCALS"
    local ali_tag="ENV_WATCHER_ALIAS"
    export ENV_WATCHER_INPUT="${env_tag}>>
$(env)
<<${env_tag}
${loc_tag}>>
$(set)
<<${loc_tag}
${ali_tag}>>
$(alias)
<<${ali_tag}
"
    local output="$( ${ENV_WATCHER_DIR}/python/env-watcher $@ )"
    unset ENV_WATCHER_INPUT

    echo "${output}"
    # echo "${output%%ENVIRONMENT_FOLLOWS*}"
    # # echo ENVIRONMENT_FOLLOWS
    # if [ ! -z "$(echo $output | grep ENVIRONMENT_FOLLOWS)" ]
    #     then
    #     eval "${output##*ENVIRONMENT_FOLLOWS}"
    # fi
    
}