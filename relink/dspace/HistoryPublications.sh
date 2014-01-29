#!/usr/bin/env bash
set -o pipefail  # trace ERR through pipes
set -o errtrace  # trace ERR through 'time command' and other functions
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value

relink_dspace() {
    newdir=$1
    olddir=$2
    ext=$3
    xpath="$4"
    #mkdir -p "$newdir"
    # http://stackoverflow.com/a/1120952/1763984 Capturing output of find . -print0 into a bash array
    unset a i
    while IFS= read -r -u3 -d $'\0' file; do
        dx=$(dirname "$file")
        filename=$(basename "$file")
        #extension="${filename##*.}"
        count=$(ls "$dx"/*.pdf | wc -w)
        hdl=$(xmllint --xpath "$xpath" $dx/dublin_core.xml)
        newfile=$(basename "$hdl")
        # if [[ $count > 1 ]]; then  # complex, link each file in a directory
        mkdir -p "$newdir/complex/$newfile"
        cd "$newdir/complex/$newfile"
        for file in "$dx/"*".$ext";
        do
            ln "$file" 
        done
        if [[ $count == 1 ]]; then            # simple
          content=$(ls "$dx"/*.pdf)
          ln "$content" $newdir/simple/$newfile.$ext
        fi
        #set -x
        #set +x
    done 3< <(find "$olddir" -name "dublin_core.xml" -type f -print0)
}

new_base_dir="/apps/content/new_path"
old_base_dir="/apps/content/raw_files"

relink_dspace \
  "$new_base_dir/UCI/UCIHistoryPublications" "$old_base_dir/UCI/UCIHistory/Publications" "pdf" \
  "/dublin_core/dcvalue[@element='identifier'][@qualifier='uri'][1]/text()"
