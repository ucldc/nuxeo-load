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

sample `application/json-nxentity`

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

## uid of file must be specified in one of 4 ways

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
