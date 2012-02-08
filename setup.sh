#
# This is setup.sh, the setup script of EnvWatcher for the Bourne Again SHell
# This file needs to be sourced. It cannot be executed.

export ENV_WATCHER_DIR="$( cd $( dirname "${BASH_SOURCE[0]}" ) && pwd )"

export ENV_WATCHER_SESSION=$(python -c "import tempfile; print tempfile.mkdtemp(prefix='EnvWatcher_session_')")

function env-watcher {
	export ENV_WATCHER_INPUT="ENV_WATCHER_LOCALS>>"$'\n'"$(set)"$'\n'"ENV_WATCHER_ALIAS>>"$'\n'"$(alias)"
	local output="$( ${ENV_WATCHER_DIR}/python/env-watcher $@ )"
	unset ENV_WATCHER_INPUT

	if [ ! -z "$( echo ${output} | grep 'CODE_FOLLOWS>>' )" ]
		then
		echo -n "${output%%CODE_FOLLOWS>>*}"
		eval "${output##*CODE_FOLLOWS>>}"
	else
		echo "${output}"
	fi
	
}

complete -o nospace -C $ENV_WATCHER_DIR/python/env_watcher_completion.py env-watcher