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
    mkdir -p "$newdir"
    # http://stackoverflow.com/a/1120952/1763984 Capturing output of find . -print0 into a bash array
    unset a i
    while IFS= read -r -u3 -d $'\0' file; do
        dx=$(dirname "$file")
        filename=$(basename "$file")
        extension="${filename##*.}"
        hdl=$(xmllint --xpath "$xpath" $dx/dublin_core.xml)
        newfile=$(basename "$hdl")
        set -x
          ln "$file" $newdir/$newfile.$extension
        set +x
    done 3< <(find "$olddir" -name "*.$ext" -type f -print0)
}

new_base_dir="/apps/content/new_path"
old_base_dir="/apps/content/raw_files"

# relink_dspace \
  # "$new_base_dir/UCI/UCIHistoryOralHistories" "$old_base_dir/UCI/UCIHistory/OralHistories" "mp3" \
  # "/dublin_core/dcvalue[@element='identifier'][@qualifier='uri'][1]/text()"

relink_dspace \
  "$new_base_dir/UCI/UCIHistoryFilmsAndVideos" "$old_base_dir/UCI/UCIHistory/FilmsAndVideos" "mp4" \
  "/dublin_core/dcvalue[@element='identifier'][1]/text()"

# relink_dspace \
#   "$new_base_dir/UCI/UCIHistoryPublications" "$old_base_dir/UCI/UCIHistory/Publications" "pdf" \
#   "/dublin_core/dcvalue[@element='identifier'][@qualifier='uri'][1]/text()"
  
relink_dspace \
  "$new_base_dir/UCI/Rorty" "$old_base_dir/UCI/Rorty" "pdf" \
  "/dublin_core/dcvalue[@element='identifier'][1]/text()"

# relink_dspace \
#  "$new_base_dir/UCI/VAOHP" "$old_base_dir/UCI/VAOHP" "pdf" \
#  "/dublin_core/dcvalue[@element='identifier'][1]/text()"
