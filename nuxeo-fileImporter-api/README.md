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

```
  841  ./loader.sh UCR UniversityArchivesPhotographs SampleCustomPicture
  847  ./loader.sh UCR TuskegeeAirmenArchive SampleCustomPicture
  932  ./loader.sh UCR SabinoOsunaPapers SampleCustomPicture
  952  bash loader.sh UCI UCIHistoryEarlyCampusPhotoAlbums SampleCustomPicture
  982  bash loader.sh UCI UCIHistorySlides SampleCustomPicture
 1011  bash loader.sh UCI UCIHistoryStaffPhotographerImages SampleCustomPicture
```
