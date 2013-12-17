nuxeo@nuxeo-stg:/apps/content/new_path> find UC* -type f | xargs -I {} bash -c 'path_get asset-library/{}' >> loaded-uuid
