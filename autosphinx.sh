#!/bin/bash
#
# autosphinx.sh - automatically generate the sphinx code documentation
#                 for a flowtool component
#
# CAVEAT: (currently) only works inside the project dirs (base/dirname foo...)
# TODO: fix that.
#

set -e

docname () {
    pyfile="$1"
    pyname=$(basename "$pyfile")
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
    find "$1" -name "*.py" | while read pyfile; do
        docname "$pyfile"
    done
}

# shellcheck disable=SC2046,SC2086
genrst () {
    star_seq=$(seq 1 "${#1}")
    stars=$(printf '*%.0s' ${star_seq})
    rst_content="Source Documentation: $1
**********************$stars

.. automodule:: $1
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
"
    echo "$rst_content"
}


PROJECT_ROOT="${1:-.}"
AUTODOC_INDEX="$PROJECT_ROOT/doc/source/docstrings/index.rst"

gendocfiles () {
    searchdir="$1"
    docdir="$2"
    if [[ ! -d "$docdir" ]]; then
        mkdir -p "$docdir"
    fi
    findmods "$searchdir" | while read line; do
        if [[ "$line" =~ ^found: ]]; then
            found="${line##found: }"

            #docfilename="$found.rst"
            docfilename="${found/\./__}.rst"
            docfile="$docdir/$docfilename"

            genrst "$found" > "$docfile"
            echo "generated: $docfile"
        fi
    done
}

gentoc () {
    toclines=$(sed 's/^/    /' <<< "$1")
    #reflines=$(sed 's/^\(.*\)/* :ref:`\1`/' <<< "$1")
    toc_file="Autogenerated Source Documentation
==================================

Contents:

.. toctree::
    :maxdepth: 2

$toclines
"
    echo "$toc_file"
}

gendocs () {
    docdir=$(dirname "$2")
    generated=$(gendocfiles "$1" "$docdir" | sed 's#generated: .*/\([^/]*\).rst#\1#' | sort)
    echo "==> Regenerated $docdir"
    gentoc "$generated" > "$2"
    echo "==> Refreshed $2"
}

gendocs "$PROJECT_ROOT" "$AUTODOC_INDEX"