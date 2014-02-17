#!/usr/bin/env bash
set -o pipefail  # trace ERR through pipes
set -o errtrace  # trace ERR through 'time command' and other functions
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value

new_base_dir="/apps/content/new_path"
old_base_dir="/apps/content/raw_files"

olddir="/apps/content/raw_files/UCR/george fujimoto diaries"
newdir="/apps/content/new_path/UCR/FujimotoDiaries"


mkdir -p "$newdir"
cd "$newdir"
# http://stackoverflow.com/a/1120952/1763984 Capturing output of find . -print0 into a bash array
unset a i
while IFS= read -r -u3 -d $'\0' file; do
    filename=$(basename "$file")
    # remove space from directory name
    newname=$(echo "$filename" | tr -d ' ')
    echo "$file, $newname"
    mkdir -p "$newname"

    while IFS= read -r -u3 -d $'\0' file2; do
        # echo $file2
        filename2=$(echo $file2 | tr '[:upper:]' '[:lower:]' | tr -d ' ')
        filename2=$(basename "$filename2")
        # echo $filename2
        #set -x
          ln "$file2" $newdir/$newname/$filename2
        #set +x
    done 3< <(find "$file" -name "*.???" -type f -print0)

done 3< <(find "$olddir"/* -type d -print0)


# done 3< <(find "$olddir" -name "*.$ext" -type f -print0)

