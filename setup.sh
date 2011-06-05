#
# This is setup.sh, the setup script of EnvWathcer for the Bourne Again SHell
# This file needs to be sourced. It cannot be executed.

previous_PWD=$PWD
previous_OLDPWD=$OLDPWD
cd $(dirname $BASH_SOURCE)
export ENV_WATCHER_DIR="$(pwd)"
cd $previous_PWD
OLDPWD=$previous_OLDPWD
unset previous_PWD
unset previous_OLDPWD

export ENV_WATCHER_SESSION=$(python -c "import tempfile; print tempfile.mkdtemp(prefix='EnvWatcher_session_')")

function env-watcher {
	export ENV_WATCHER_INPUT="ENV_WATCHER_ENVIRONMENT>>
$(env)
ENV_WATCHER_LOCALS>>
$(set)
ENV_WATCHER_ALIAS>>
$(alias)
"
	local output="$( ${ENV_WATCHER_DIR}/python/env-watcher $@ )"
	unset ENV_WATCHER_INPUT

	if [ ! -z "$( echo ${output} | grep 'CODE_FOLLOWS>>' )" ]
		then
		echo -n "${output%%CODE_FOLLOWS>>*}"
		# echo "Now comes code:"
		# echo "${output##*CODE_FOLLOWS>>}"
		eval "${output##*CODE_FOLLOWS>>}"
	else
		echo "${output}"
	fi
	
}