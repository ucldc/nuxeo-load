def nuxeo_mapper(docs, nx):
    for doc in docs:
        identifier = doc['properties']['ucldc_schema:identifier']
        localidentifiers = doc['properties']['ucldc_schema:localidentifier']  # array
        newproperties = {}
        if identifier:
            newproperties['ucldc_schema:identifier'] = None
            newproperties['ucldc_schema:localidentifier'] = localidentifiers
            newproperties['ucldc_schema:localidentifier'].append(identifier)
            doc['properties'] = newproperties
            nx.update_nuxeo_properties(doc, uid=doc['uid'])
