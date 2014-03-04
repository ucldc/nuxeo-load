#!/usr/bin/env bash
set -eu

#dirs=(/apps/content/new_path/UCR/SabinoOsunaPapers/box_013\
#dirs=(/apps/content/new_path/UCR/SabinoOsunaPapers/box_014\
dirs=(/apps/content/new_path/UCR/SabinoOsunaPapers/box_015\
 /apps/content/new_path/UCR/SabinoOsunaPapers/box_016\
 /apps/content/new_path/UCR/SabinoOsunaPapers/box_017\
 /apps/content/new_path/UCR/SabinoOsunaPapers/box_018\
 /apps/content/new_path/UCR/SabinoOsunaPapers/box_019\
 /apps/content/new_path/UCR/SabinoOsunaPapers/box_020)

for folder in ${dirs[*]} 
do
  pifolder \
    --leaf_type SampleCustomPicture \
    --input_path $folder \
    --target_path asset-library/UCR/SabinoOsunaPapers \
    --folderish_type Organization \
    --poll_interval 5
done
