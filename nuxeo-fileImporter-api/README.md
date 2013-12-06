# api security

Change the default password for the `Administrator` account.  Then, to use the command line API wrapper 
```bash
export NUXEO_ADMIN_PASS="my_new_password"
```

to run a command

```
. nuxeo-fileImporter-api.sh # adds `api_get` function to path
api_get log
api_get status
```

to load a collection

```
bash loader.sh campus collection leafType
```
