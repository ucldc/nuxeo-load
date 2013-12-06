#!/usr/bin/env bash
set -o pipefail  # trace ERR through pipes
set -o errtrace  # trace ERR through 'time command' and other functions
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value

project="Rorty"

newdir="/apps/content/new_path/UCI/$project"

mkdir -p "$newdir"

# http://stackoverflow.com/a/1120952/1763984 Capturing output of find . -print0 into a bash array
unset a i
while IFS= read -r -u3 -d $'\0' file; do
    dx=$(dirname "$file")
    filename=$(basename "$file")
    extension="${filename##*.}"
    newfile=$(basename "$dx")
    set -x
    ln "$file" $newdir/$newfile.$extension
    set +x
done 3< <(find /apps/content/raw_files/UCI/$project/ -name "*.pdf" -type f -print0)
