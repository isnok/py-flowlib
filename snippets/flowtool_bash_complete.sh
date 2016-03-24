_flowtool_completion() {
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _FLOWTOOL_COMPLETE=complete $1 ) )
    return 0
}

complete -F _flowtool_completion -o default flowtool;

_ft_completion() {
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _FT_COMPLETE=complete $1 ) )
    return 0
}

complete -F _ft_completion -o default ft;
