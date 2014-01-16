# `update_one`

```
usage: update_one [-h] [--uid UID | --path PATH] file

nuxeo metadata via REST API, one record

positional arguments:
  file         application/json+nxentity

optional arguments:
  -h, --help   show this help message and exit
  --uid UID    update specific nuxeo uid
  --path PATH  update specific nuxeo path
```

## success
json on `STDOUT` will be response of `PUT` from nuxeo REST API and exit code will be 0.

## failure
sould exit with a non-zero exit code, relevent error message should be near the end of the output

## sample `application/json+nxentity` json

```json
{
  "uid": "0119ec23-7102-4181-8b88-9987ce4d6594",
  "properties": {
    "ucldc_schema:alternativetitle": [
      "alternative title"
    ]
  },
  "path": "/asset-library/UCI/Rorty/1000.pdf"
}
```

Only the properties part of the json object is taken into account for update.  

## authentication
```bash
export NUXEO_API_PASS="Administrator"
```

don't keep credentials in revision control

## uid of file must be specified in one of 4 ways

updating a nuxeo document's properties must specify a uid of the document.  If you don't know
the uid; this can be looked up from the document path.  Nuxeo document uid or path can be specified in the 
json or on the command line.

### `"uid":` in json file
if a uid is in the json file; this will be used 

### `--uid` on command line
uid supplied on command line will override `"uid":` or `"path":`
in the json file

### `"path":` in json
if no uid is supplied, path can be used to look up the uid

### `--path` on command line
path supplied on command line will override `"uid":` or `"path":`
in the json file
