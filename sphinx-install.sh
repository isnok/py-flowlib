#!/bin/bash
#
# a quick-and-dirty automatisation of the sphinx-quickinstall process
# for flowtool component dorectories
#

set -e

COMPONENT_DIR="${1:-.}"

cd "$COMPONENT_DIR"

project_name=$(python -c "import setup; print(setup.setup_args['name'])")
project_version=$(./versioning.py | sed 's/+.*//')

docdir="doc"

quickstart_input="$docdir
y

$project_name
Konstantin Martini
$project_version


.rst

n
y

y

y

y
y
y
y
y
"

read -n1 -p "Press any key to update docs for $project_name ($project_version) ..."
sphinx-quickstart <<< "$quickstart_input"

echo "Adding 'docstrings/index' to index.rst"
docindex="$docdir/source/index.rst"
if ! grep docstrings/index "$docindex"; then
    # shellcheck disable=SC1004
    sed -i '12a\
    docstrings/index' "$docindex"
fi

echo "Done."
