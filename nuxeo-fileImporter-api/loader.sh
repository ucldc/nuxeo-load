#!/usr/bin/env bash
set -o pipefail  # trace ERR through pipes
set -o errtrace  # trace ERR through 'time command' and other functions
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # http://stackoverflow.com/questions/59895
. $DIR/nuxeo-fileImporter-api.sh

campus=$1
collection=$2
leafType=$3

api_get "logActivate"
api_get "run?leafType=$leafType&inputPath=/apps/content/new_path/$campus/$collection&targetPath=asset-library/$campus&folderishType=Organization"
api_get "status"
api_get "log"
