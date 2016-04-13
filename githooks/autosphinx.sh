#!/bin/bash
#
# autosphinx.sh - automatically generate the sphinx code documentation
#                 for a flowtool component
#

modname () {
    pyfile="$1"
    package=$(basename $(dirname $pyfile))
    if [[ "$package" =~ ^flowtool ]]; then
        pyname=$(basename $pyfile)
        module="${pyname%%.py}"
        echo "found: $found"
    else
        echo "ignore: $pyfile"
    fi
}

docname () {

    pyfile="$1"
    pyname="$(basename $pyfile)"
    module="${pyname%%.py}"

    if [[ "$pyfile" =~ flowtool ]]; then
        package="${pyfile/.*flowtool/flowtool}"
        package="${package%%.py}"
        package="${package%%/__init__}"
        package="${package/\//.}"
        echo "found: $package"
    else
        echo "ignore: $module ($pyfile)"
    fi
}


findmods () {
    find $1 -name "*.py" | while read pyfile; do
        docname "$pyfile"
    done
}

findmods "${1:-.}"
