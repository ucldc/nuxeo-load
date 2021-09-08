import sys
import os
import argparse
import json
from collections import Counter

# ucldc_schema https://gist.github.com/tingletech/eac8aa1018a9af2822db07bbcdae5234

SETS = {
    'hdl_10575_1093': {
        'title': 'The Portable Rousseau by Paul de Man',
        'description': 'In 1972 Paul de Man was contracted by Viking Press to edit a collection of texts by Jean-Jacques Rousseau for their Portable readers series. Paul de Man and his wife Patricia spent the next ten years working on the translations for this volume. The collection remained incomplete at the time of Paul de Man’s death in 1983. The presentation here of The Portable Rousseau is based on extant translations by the De Mans and related editorial papers by Paul de Man. The Portable Rousseau was digitized under the direction of Professor Martin McQuillan with a grant from the British Academy. The Paul de Man papers are available for research in the Special Collections and Archives Reading Room at the UC Irvine Libraries and are described in a finding aid  in the Online Archive of California.',
        'nuxeo_folder': '/asset-library/UCI/SCA_CriticalTheoryArchives/MS-C004',
        },
    'hdl_10575_1091': {
        'title': 'Textual Allegories by Paul de Man',
        'description': 'The only contiguous, single subject monograph written by de Man during his lifetime, Textual Allegories was written in Zurich in 1973-1974 while Paul de Man was on sabbatical from Yale University. The manuscript was never published by de Man but rather formed the material for later substantially revised published versions in journal articles and notably in the second half of Allegories of Reading: Figural Language in Rousseau, Nietzsche, Rilke and Proust (1979). However, the two texts differ in significant ways line-by-line and page-by-page. Textual Allegories was digitized and transcribed under the direction of Professor Martin McQuillan with a grant from the United Kingdom, Arts and Humanities Research Council. The transcription is by Dr. Erin Obodiac. The Paul de Man papers are available for research in the Special Collections and Archives Reading Room at the UC Irvine Libraries and are described in a finding aid in the Online Archive of California.',
        'nuxeo_folder': '/asset-library/UCI/SCA_CriticalTheoryArchives/MS-C004'
        },
    'hdl_10575_13302': {
        'title': 'Veronique Saunier\'s "Still Lives" Collection',
        'nuxeo_folder': '/asset-library/UCI/SCA_SoutheastAsianArchives/MS-SEA055'
        },
    'hdl_10575_1657': {
        'title': 'Raymond L. Watson born digital writings, 1992-2010',
        'description': 'The Raymond Watson born digital writings, 1992-2010 subcollection consists of 54 digital files. Included are writings pertaining to Irvine Company developments in Orange County, California; the planning and development of the University of California, Irvine and the City of Irvine; city planning; community planning; and planned communities. Also included are reports and writings not authored by Watson that primarily relate to urban planning and design.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-R120/Raymond L. Watson born digital writings, 1992-2010'
        },
    'hdl_10575_1659': {
        'title': 'Raymond L. Watson slides on Irvine Company developments in Newport Beach, California and Irvine, California, before 1997',
        'description': 'The Raymond L. Watson slides on Irvine Company developments in Newport Beach, California and Irvine, California, before 1997 subcollection contains 95 images showing views of Newport Beach, California and Irvine, California, though the primary focus is on Newport Beach. Included are aerial and plan views of Newport Beach, as well as of Newport Center, an Irvine Company development located in Newport Beach. Also included are exterior and interior views of other Irvine Company developments, and several images pertaining to Irvine, California, such as copy prints of land use maps. The slides were digitized between 1996 and 1997 and do not necessarily reflect the date the original slides were created.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-R120/Raymond L. Watson slides on Irvine Company developments in Newport Beach, California and Irvine, California, before 1997'
        },
    'hdl_10575_1660': {
        'title': 'Raymond L. Watson slides on the Irvine Ranch, before 1997',
        'description': 'The Raymond L. Watson slides on the Irvine Ranch, before 1997 subcollection contains 88 images pertaining to the history and development of the Irvine Ranch in Orange County, California. Subjects include the Irvine family, the Irvine family home, the agricultural history of the Irvine Ranch, and the Irvine General Plan. Included are interior and exterior views of the Irvine family home, portraits of James Irvine, various views of crops and agricultural scenes on Irvine Ranch land, and maps, plans, and charts from the Irvine General Plan. Most of the maps relate to land use or population in Orange County, California. The slides were digitized between 1996 and 1997 and do not necessarily reflect the date the original slides were created.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-R120/Raymond L. Watson slides on the Irvine Ranch, before 1997'
        },
    'hdl_10575_1658': {
        'title': 'Raymond L. Watson slides on the University of California, Irvine, before 1997',
        'description': 'The Raymond L. Watson slides on the University of California, Irvine, before 1997 subcollection contains 51 images relating to the planning and development of the University of California, Irvine (UCI) campus. Included are aerial and plan views of UCI; exterior views of the UCI campus and vicinity; and maps, charts, and graphs pertaining to a university and community study to build a new University of California campus in Orange County, California. The images document the development of Irvine Ranch land to build the University of California, Irvine, campus, circa 1965-1995. The slides were digitized between 1996 and 1997 and do not necessarily reflect the date the original slides were created.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-R120/Raymond L. Watson slides on the University of California, Irvine, before 1997'
        },
    'hdl_10575_1662': {
        'title': 'Raymond L. Watson slides on various Irvine Company developments, before 1997',
        'description': 'The Raymond L. Watson slides on various Irvine Company developments, before 1997 subcollection consists of 42 images showing views of various Irvine Company developments, views of the Irvine Ranch, copy prints of various planning records, and maps of Orange County, California. Included are aerial, plan, exterior, and distant views. The images of maps are copy prints, primarily of land use maps. Though this collection includes some images of non-residential developments, many of the images document various Irvine Company residential developments, such as Woodbridge and Northwood, both located in Irvine, California. The slides were digitized between 1996 and 1997 and do not necessarily reflect the date the original slides were created.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-R120/Raymond L. Watson slides on various Irvine Company developments, before 1997'
        },
    'hdl_10575_1661': {
        'title': 'Raymond L. Watson slides on Woodbridge, Irvine, California, before 1997',
        'description': 'The Raymond L. Watson slides on Woodbridge, Irvine, California, before 1997 subcollection consists of 85 images documenting various stages in the planning and construction of Woodbridge, an Irvine Company housing development and community, circa 1970 to 1995. Included are aerial and exterior views of Woodbridge, as well as images of numerous planning documents such as schematic design drawings and land use plans. Views of the Woodbridge lakes, bridge, landscaping, and signage are also represented in this group. The slides were digitized between 1996 and 1997 and do not necessarily reflect the date the original slides were created.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-R120/Raymond L. Watson slides on Woodbridge, Irvine, California, before 1997'
        },
    'hdl_10575_11955': {
        'title': 'Susan R. Braunwald Language Acquisition Diaries',
        'description': 'This collection is comprised of diaries created by Susan R. Braunwald documenting her second child\'s acquisition of American English between late infancy (8-months) and early childhood (50-months). The diaries are redacted photocopied versions that are otherwise exact copies of the originals. The handwritten diaries contain information about an inclusive process of language acquisition that encompasses pragmatics, semantics, and syntax and is considered the "most complete diary in existence of one child\'s development of complex syntax." The daily entries from 12-to-48 months including detailed contextual and developmental notes make these data useful for research in child language and more broadly in many academic disciplines. The daily observations of L’s emergent language describe the developmental transition from the zenith of a constrained and child-specific protolanguage to the first tentative production of many English words. The emergent form of a verb, a vocabulary spurt and displacement—the need to talk about a topic other than one present in the immediate environment—were the overt milestones during the transition from a protolanguage to a natural language. Braunwald’s annotation, data analyses and interpretative hypotheses are included. The data included in this journal may be of interest to researchers in other academic disciplines, including social sciences (e.g., psychology, education, etc.) and any one searching for a longitudinal description of language development in a single child. This collection is referenced by the Braunwald-Max Planck Corpus CHILDES American English, http://childes.psy.cmu.edu',
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-F040'
        },
    'hdl_10575_1597': {
        'title': 'Interviews with Bill Cloonan, Tung Trinh, and Lam Phan in Japan',
        'description': 'This subcollection contains interviews by Duc Nguyen with Bill Cloonan, former US Navy Petty Officer of the USS Dubuque, as well as Tung Trinh and her son Lam Phan, Bolinao 52 survivors, for the documentary Bolinao 52.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SoutheastAsianArchives/MS-SEA042/PUBLISH/Interviews with Bill Cloonan, Tung Trinh, and Lam Phan in Japan'
        },
    'hdl_10575_1598': {
        'title': 'Interviews with Tung Trinh, Carlos "Caloy" Cagusaan, and others in the Philippines',
        'description': 'This subcollection contains interviews by Duc Nguyen with Tung Trinh, Bolinao 52 survivor, and films Trinh talking with the mayor, police, and hospital staff in the town of Bolinao, Philippines. In addition, Nguyen interviews rescuer Carlos Cagusaan with translator Ben Rafanan. Included is footage of a gratitude plaque ceremony and memorial, as well as an exit interview with Trinh before leaving the Philippines. Footage and interviews were recorded for the documentary Bolinao 52.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SoutheastAsianArchives/MS-SEA042/PUBLISH/Interviews with Tung Trinh, Carlos "Caloy" Cagusaan, and others in the Philippines'
        },
    'hdl_10575_1594': {
        'title': 'Interview with Bill Cloonan in California',
        'description': 'This subcollection contains interviews by Duc Nguyen with Bill Cloonan, former US Navy Petty Officer of the USS Dubuque, for the documentary Bolinao 52.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SoutheastAsianArchives/MS-SEA042/PUBLISH/Interview with Bill Cloonan in California'
        },
    'hdl_10575_1599': {
        'title': 'Interview with Tung Trinh in California',
        'description': 'This subcollection contains interviews by Duc Nguyen with Tung Trinh, Bolinao 52 survivor, for the documentary Bolinao 52.',
        'nuxeo_folder': '/asset-library/UCI/SCA_SoutheastAsianArchives/MS-SEA042/PUBLISH/Interview with Tung Trinh in California'
        },
    'hdl_10575_1338': {
        'title': 'Mark Poster administrative records for the Critical Theory Institute at the University of California, Irvine, 1988-1999',
        'description': 'This subcollection includes administrative files such as agendas, minutes, correspondence, annual reports, and speaker introductions associated with Mark Poster\'s work with the Critical Theory Institute (CTI). Researchers must submit an application to use this subcollection and agree to follow the Rules of Use for the Virtual Reading Room. Access may be granted in less than 5 business days.',
        'nuxeo_folder': '/asset-library/UCI/SCA_CriticalTheoryArchives/MS-C018/Born digital files, 1985-2009/Administrative records for the Critical Theory Institute at the University of California, Irvine, 1988-1999'
        },
    'hdl_10575_1337': {
        'title': 'Mark Poster book drafts, 1988-2009',
        'description': 'This subcollection consists of ten sub-directories from Mark Poster\'s original files, including drafts, notes, email correspondence, and other documents related to his book publications. Each sub-directory has been appraised and packaged for access as a .zip file by the UCI Libraries. The .zip files reflect almost all of the files on Mark Poster\'s hard drive and his original organizational scheme. Researchers may search the contents of the .zip files after downloading and unzipping them. Each .zip file is accompanied by a .csv file that lists the contents of the .zip file. Only the .csv file is searchable within UCISpace. This .csv file may be opened using a spreadsheet program such as Microsoft Excel.',
        'nuxeo_folder': '/asset-library/UCI/SCA_CriticalTheoryArchives/MS-C018/Born digital files, 1985-2009/Book drafts, 1988-2009'
        },
    'hdl_10575_1339': {
        'title': 'Mark Poster lectures, 1986-2007',
        'description': 'This subcollection consists of course descriptions, syllabi, course materials, and other documents related to Mark Poster\'s lectures on European intellectual and cultural history, critical theory, and media studies.',
        'nuxeo_folder': '/asset-library/UCI/SCA_CriticalTheoryArchives/MS-C018/Born digital files, 1985-2009/Lectures, 1986-2007'
        },
    'hdl_10575_1340': {
        'title': 'Mark Poster research files, 1985-2008',
        'description': 'This subcollection consists of three directories from Mark Poster\'s original files, including correspondence, research articles, citations, reviews, and other documents related to Poster\'s scholarly interests. Each directory has been appraised and packaged for access as a .zip file by the UCI Libraries. The .zip files reflect almost all of the files on Mark Poster\'s hard drive and his original organizational scheme. Researchers may search the contents of the .zip files after downloading and unzipping them. Each .zip file is accompanied by a .csv file that lists the contents of the .zip file. Only the .csv file is searchable within UCISpace. This .csv file may be opened using a spreadsheet program such as Microsoft Excel. "Notes" and "Publications" are restricted. Researchers must submit an application to use the content and agree to follow the Rules of Use for the Virtual Reading Room. Access may be granted in less than 5 business days.',
        'nuxeo_folder': '/asset-library/UCI/SCA_CriticalTheoryArchives/MS-C018/Born digital files, 1985-2009/Research files, 1985-2008'
        },
    'hdl_10575_2395': {
        'title': 'Frank Cancian photographs for Main Street UCI, 2009',
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-154/Frank Cancian photographs for Main Street UCI, 2009'
        },
    'hdl_10575_3348': {
        'title': 'Frank Cancian photographs for Main Street UCI, 2010',
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-154/Frank Cancian photographs for Main Street UCI, 2010'
        },
    'hdl_10575_2093': {
        'title': 'Frank Cancian photographs for Main Street UCI, 2011',
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-154/Frank Cancian photographs for Main Street UCI, 2011'
        },
    'hdl_10575_1096': {
        'title': 'Hugh Everett III Biographical Materials',
        'nuxeo_folder': '/asset-library/UCI/DSS_Collections/Hugh Everett III manuscripts/Publish/Biographical materials'
        },
    'hdl_10575_1097': {
        'title': 'Hugh Everett III Correspondence',
        'nuxeo_folder': '/asset-library/UCI/DSS_Collections/Hugh Everett III manuscripts/Publish/Correspondence'
        },
    'hdl_10575_1098': {
        'title': 'Hugh Everett III Research on Game Theory, Decision Theory, and Other Topics',
        'nuxeo_folder': '/asset-library/UCI/DSS_Collections/Hugh Everett III manuscripts/Publish/Research on Game Theory, Decision Theory, and other topics'
        },
    'hdl_10575_1223': {
        'title': 'Hugh Everett III Thesis, Quantum Mechanics, and Related Materials',
        'nuxeo_folder': '/asset-library/UCI/DSS_Collections/Hugh Everett III manuscripts/Publish/Thesis, quantum mechanics, and related materials'
        },
    'hdl_10575_10877': {
        'title': 'Frank Cancian documentary photographs of Zinacantan, Mexico, 1971',
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-F034/Zinacantan'
        },
}

LANGUAGES = {
    'en_US': {
        'name': 'English',
        'code': 'eng'
    }
}

TYPES = {
    'application/pdf': {
        'ucldc_schema:type': 'text',
        'nuxeo_doc_type': 'CustomFile'
    },
    'audio/mpeg': {
        'ucldc_schema:type': 'sound',
        'nuxeo_doc_type': 'CustomAudio'
    },
    'application/vnd.ms-excel': {
        'ucldc_schema:type': 'dataset',
        'nuxeo_doc_type': 'CustomFile'
    },
    'image/jpeg': {
        'ucldc_schema:type': 'image',
        'nuxeo_doc_type': 'SampleCustomPicture'
    },
    'video/quicktime': {
        'ucldc_schema:type': 'movingimage',
        'nuxeo_doc_type': 'CustomVideo'
    },
    'application/msword': {
        'ucldc_schema:type': 'text',
        'nuxeo_doc_type': 'CustomFile'
    },
    'application/octet-stream': {
        'ucldc_schema:type': 'text',
        'nuxeo_doc_type': 'CustomFile'
    },
    'text/csv': {
        'ucldc_schema:type': 'dataset',
        'nuxeo_doc_type': 'CustomFile'
    },
    'application/x-photoshop': {
        'ucldc_schema:type': 'image',
        'nuxeo_doc_type': 'SampleCustomPicture'
    }
}

def main():
    parser = argparse.ArgumentParser(
        description='Map metadata to ucldc schema and write to jsonl file')
    parser.add_argument('setid', help="OAI-PMH set id")
    argv = parser.parse_args()

    setid = argv.setid

    metadata_file = f"json_files/{setid}-unmapped-md.jsonl"

    # read in jsonl file
    with open(metadata_file) as mf:
        data = json.load(mf)

    # payload file
    payload_file = f"json_files/{setid}-payload.jsonl"
    if os.path.exists(payload_file):
        os.remove(payload_file)

    items = []
    for record in data:

        properties = {}

        # title
        properties['dc:title'] = record.get('title')[0]

        # alternative titles
        if len(record.get('title')) > 1:
            alt_titles = record.get('title')[1:]
            properties['ucldc_schema:alternativetitle'] = alt_titles

        # contributor
        if record.get('contributor'):
            contribs = []
            for contributor in record.get('contributor'):
                name = contributor
                nametype = 'persname'
                contribs.append({'name': name, 'nametype': nametype})
            if len(contribs) > 0:
                properties['ucldc_schema:contributor'] = contribs

        # creator
        if record.get('creator'):
            creators = []
            for creator in record.get('creator'):
                name = creator
                nametype = 'persname'
                creators.append({'name': name, 'nametype': nametype})
            if len(creators) > 0:
                properties['ucldc_schema:creator'] = creators

        # created date
        # for some sets, coverage field contains date created
        if record.get('coverage') and setid != 'hdl_10575_10877':
            coverage = record.get('coverage')[0]
            coverage = coverage[:10]
            properties['ucldc_schema:date'] = [{'date': coverage, 'datetype': 'created'}]
        elif record.get('date'):
            dates_created = []
            for d in record.get('date'):
                dates_created.append({'date': d, 'datetype': 'created'})
            properties['ucldc_schema:date'] = dates_created


        # descriptions
        descriptions = []
        # add dc:description
        if record.get('description'):
            for desc in record.get('description'):
                descriptions.append({'item': desc, 'type': 'scopecontent'})
        # add OAI-PMH set description
        if SETS[setid].get('description'):
            set_description = SETS[setid]['description']
            descriptions.append({'item': set_description, 'type': 'scopecontent'})
        # add dc:relation
        if record.get('relation'):
            relations = [{'item': relation, 'type': 'scopecontent'} for relation in record.get('relation')]
            descriptions.append(relations[0])
        properties['ucldc_schema:description'] = descriptions


        # local identifier
        local_ids = [identifier for identifier in record.get('identifier')]
        properties['ucldc_schema:localidentifier'] = local_ids

        # language
        if record.get('language'):
            languages = []
            for language in record.get('language'):
                if language == 'other' and setid in ['hdl_10575_1598', 'hdl_10575_1599']:
                    languages.append(
                        {
                            'language': 'Vietnamese',
                            'languagecode': 'vie'
                        }
                    )
                    languages.append(
                        {
                            'language': 'English',
                            'languagecode': 'eng'
                        }
                    )
                else:
                    languages.append(
                        {
                            'language': LANGUAGES[language]['name'], 
                            'languagecode': LANGUAGES[language]['code']
                        }
                    )
            properties['ucldc_schema:language'] = languages

        # publisher
        if record.get('publisher'):
            publishers = [publisher for publisher in record.get('publisher')]
            properties['ucldc_schema:publisher'] = publishers

        # add OAI-PMH set title to relatedresource field
        set_title = SETS[setid]['title']
        properties['ucldc_schema:relatedresource'] = [set_title]

        # rights
        rights_statements = [rights for rights in record.get('rights')]
        if len(rights_statements) > 0:
            rights_statement = '\n'.join(rights_statements)
            properties['ucldc_schema:rightsstatement'] = rights_statement

        # subjects
        if record.get('subject'):
            subjects = []
            for subject in record.get('subject'):
                subjects.append({'heading': subject}) # no headingtype?
            properties['ucldc_schema:subjecttopic'] = subjects

        # type - not a repeating field in ucldc_schema, so hopefully there's just one in the source
        valid_types = ['dataset', 'image', 'movingimage', 'physicalobject', 'software', 'sound', 'text']
        if record.get('type'):
            for type in record.get('type'):
                if type in valid_types:
                    properties['ucldc_schema:type'] = type
                else:
                    # TODO: infer type from mimetype
                    item_type = get_item_type(record)
                    properties['ucldc_schema:type'] = item_type
        else:
            item_type = get_item_type(record)
            properties['ucldc_schema:type'] = item_type

        '''
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(properties)
        '''
        
        # INSERT MIMETYPE AND NUXEO DOC TYPE
        component_count = 0
        for component in record.get('component_resources'):
            component_count = component_count + 1
            mimetype = component['mimeType']
            component['ucldc_schema:type'] = TYPES[mimetype]['ucldc_schema:type']
            component['nuxeo_doc_type'] = TYPES[mimetype]['nuxeo_doc_type']

        # infer nuxeo doc type from mimetype
        # if there's a parent object, infer nuxeo doc type from its mimetype
        # elif there are component objects, infer nuxeo doc type from most frequent mimetype
        # else CustomFile ? Or can we get a default type for the collection?
        nuxeo_doc_type = get_doc_type(record)

        # ARRANGE CONTENT FILE INFO ACCORDING TO WHETHER SIMPLE OR COMPLEX
        record['content_files'] = {}
        if component_count == 1:
            record['content_files']['main'] = record['component_resources']
        elif component_count > 1:
            record['content_files']['components'] = record['component_resources']

        items.append(
                {
                    'properties': properties, 
                    'content_files': record['content_files'],
                    'nuxeo_folder': SETS[setid]['nuxeo_folder'],
                    'nuxeo_doc_type': nuxeo_doc_type
                }
            )


    with open(payload_file, 'a') as f:
        f.write(f"{json.dumps(items)}\n")

def get_item_type(record):
    mimetypes = [component['mimeType'] for component in record.get('component_resources')]
    '''
    if len(mimetypes) > 0:
        dominant_type = most_frequent(mimetypes)
    else:
        dominant_type = 'application/pdf' # if there are no content files, default to text
    '''
    dominant_type = most_frequent(mimetypes)
    return TYPES[dominant_type]['ucldc_schema:type']

def get_doc_type(record):
    mimetypes = [component['mimeType'] for component in record.get('component_resources')]
    '''
    if len(mimetypes) > 0:
        dominant_type = most_frequent(mimetypes)
    else:
        dominant_type = 'application/pdf' # if there are no content files, default to text
    '''
    dominant_type = most_frequent(mimetypes)
    return TYPES[dominant_type]['nuxeo_doc_type']

def most_frequent(List):
    ''' will abitrarily return one of the winners if there's a tie '''
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]

if __name__ == '__main__':
    sys.exit(main())