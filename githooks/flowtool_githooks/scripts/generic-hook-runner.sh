#!/bin/bash

HOOK_NAME="$(basename $0)"

HELP="
This script runs all executable hooks from the respective directory.
It changes its behaviour based on the name it is invoked with ($HOOK_NAME).
It should not be necessary to run it manually.
"

give_help () {
    echo "$HELP"
}

echo_color () {
    echo -en "$1"
    shift
    echo "$@"
    echo -en "\e[0m"
}

echo_mark () {
    color="$1"
    shift
    echo_color "$color" -n "== git-hook = $HOOK_NAME => "
    echo_color "$color" "$@"
}

#echo_info () { echo_mark "\e[1m" "$@"; }
echo_info () { echo_mark "" "$@"; }
echo_nice () { echo_mark "\e[1m\e[32m" "$@"; }
echo_warn () { echo_mark "\e[1m\e[33m" "$@"; }
echo_fail () { echo_mark "\e[1m\e[31m" "$@"; }

exit_nice () {
    echo_info "$@"
    exit 0
}
exit_fail () {
    ret=$1
    shift
    echo_fail "$@" "($ret)"
    exit $ret
}

run_hook () {
    hook="$(basename $1)"
    echo_info "$hook"
    run="$1"
    shift
    if [[ -f "$STDIN_TMPFILE" ]]; then
        cat "$STDIN_TMPFILE" | $run "$@"
    else:
        $run "$@"
    fi
}

hook_done () {
    if [[ $1 -ne 0 ]]; then
        exit_fail $1 "failed: $2"
    fi
}

STDIN_TMPFILE=""

clean_tempiles () {
    rm "$STDIN_TMPFILE"
}

save_stdin () {
    if [[ -t 0 ]]; then
        stty -echo -icanon time 0 min 0
    fi

    read line
    if [[ -n "$line" ]]; then

        STDIN_TMPFILE=$(mktemp "/tmp/$HOOK_NAME-XXXXXX")
        trap clean_tempiles EXIT SIGINT

        while [[ -n "$line" ]]; do
            echo "$line" >> $STDIN_TMPFILE
            read line
        done
    fi

    if [[ -t 0 ]]; then
        stty sane
    fi
}

run_hooks () {
    GIT_DIR="$(git rev-parse --git-dir)"
    HOOK_DIR="${GIT_DIR}/hooks/${HOOK_NAME}.d"
    mkdir -p "$HOOK_DIR"
    HOOKS=$(find "$HOOK_DIR" -executable -not -type d | sort -nr)
    save_stdin
    for hook in $HOOKS; do
        run_hook "$hook" "$@"
        ret=$?
        hook_done $ret "$hook" "$@"
    done
    if [ -n "$HOOKS" ]; then
        exit_nice "done."
    fi
}

case "$HOOK_NAME" in
    generic-hook-runner.sh)
        give_help
        ;;
    flowtool-*)
        give_help
        ;;
    *)
        run_hooks "$@"
        ;;
esac
