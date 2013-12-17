# change the default password and don't commit to revision control
NUXEO_ADMIN_PASS=${NUXEO_ADMIN_PASS="Administrator"}

path_get() {
  uid=$(curl -s --basic -u "Administrator:$NUXEO_ADMIN_PASS" "http://localhost:8080/nuxeo/api/v1/path/$1" | jq ".uid")
  echo "$1	$uid"
}



