# change the default password and don't commit to revision control
NUXEO_ADMIN_PASS=${NUXEO_ADMIN_PASS="Administrator"}

api_get() {
  echo "$1:"
  curl --basic -u "Administrator:$NUXEO_ADMIN_PASS" "http://localhost:8080/nuxeo/site/fileImporter/$1"
  echo ""
}

