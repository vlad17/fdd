#!/bin/bash
# ./scripts/format.sh [--check]
# automatically formats all files in place

set -e

if [ "$1" = "--check" ] ; then
    black --line-length 79 --py36 --verbose --check tasque
    sed -ns '${/./F}' **/*.{py,sh}
    isort -rc --diff .
else
    black --line-length 79 --py36 --verbose tasque
    sed -i -e '$a\' **/*.{py,sh}
    isort -rc --atomic .
fi
