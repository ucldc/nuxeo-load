#! /usr/bin/env python
from pynux import utils
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
import json

''' write nuxeo uid, identifier to file for UCSF Berne collections '''
collections = [
                  #'/asset-library/UCSF/Berne_Eric_Collection',
                  '/asset-library/UCSF/MSS 2003-12 Eric Berne papers',
                  '/asset-library/UCSF/MSS 2005-08 Eric Berne papers',
                  '/asset-library/UCSF/MSS 2013-18 Eric Berne papers',
                  '/asset-library/UCSF/MSS 2013-19 Eric Berne papers',
                  '/asset-library/UCSF/MSS 82-0 Eric Berne papers',
                  '/asset-library/UCSF/MSS 89-12 Eric Berne papers'
              ]


map = {}
for collection in collections:
    dh = DeepHarvestNuxeo(collection, '')
    objects = dh.fetch_objects()
    for obj in objects:
        uid = obj['uid']
        filename = obj['path'].split('/')[-1]
        identifier = filename.split('.')[0]
        map[identifier] = uid 

# Additions
map['mss2005-08_1_7_CTmedapplication_1937-08-02'] = 'bef32337-6ca6-43c9-9eaa-e0553f26f3dc'
map['mss2013-19_5_17_difficulties-comparative-psychiatry_ca1959'] = 'ad8c13d2-a89d-4346-809b-03cd612b9c80'
map['mss2013-19_18_CAboardmedexaminers-cert_1945-07-19'] = 'ad8c13d2-a89d-4346-809b-03cd612b9c80'
map['mss82-0_cover_gamespeopleplay-Israeli-ed'] = '13d32c79-0e59-4b25-b590-08c3249ca420'
map['mss2005-08_1_13_AUS-certofservice_1946-09-23'] = '74a79291-43b4-4ae0-9d56-634ee1a5953c'
map['mss2013-19_1_2_statement-interests-activities_ca1937'] = 'a52a3ab2-8c2b-48d0-b082-969e6cb6dcc3'
map['mss82-0_cover_juegos-en-que-participamos001'] = 'ec8a4de2-e65d-4963-9af2-6693fef19763'
map['mss2013-19_4_6_travelephemera_turkeytckt_002'] = '231291e7-91af-4fee-8c06-0bebb817a899'
map['mss2003-12_5_9_sexinhumanlivingdiagram_ca1966'] = 'ed8ee034-f82b-4d63-a5f0-d2c03f363702'

# Overrides
map['mss2003-12_1_1_letterfromKinsey_1955-10-15'] = 'fe41023f-9aa0-4773-82e9-99b2f88b1652'
map['mss2003-12_7_16_scriptanalysis-psychotherapy-titlepage_1970'] = '4870b245-4554-4fdb-a568-f4089b7f739d'
map['mss2003-12_7_4_structure-dynamics-orgs-groups-drawing143ab_undated'] = '5c20ec09-a216-46ce-a031-116fb86ad7b3'
map['mss2003-12_7_4_structure-dynamics-orgs-groups-drawing26_undated'] = 'e32ad117-f627-4737-bef0-79c10e33f929'
map['mss2003-12_7_5_structure-dynamics-orgs-groups-drawing22c_undated'] = '02fcdf9f-199b-4235-b4f2-fb9eb25b314a'
map['mss2003-12_7_8_TA-psychotherapy-diagram-fig16_ca1964'] = 'b79249e8-cdee-4792-ab11-5778dd1deff9'
map['mss2005-08_4_22_NYTimesBestsellerList_1966-07-24'] = '3afc8d5a-5949-4030-82a1-b731028373c5'
map['mss2003-12_8_11_AGPAWesternRegMeeting_1957-11'] = 'cd1d3695-2cf1-46e4-b81c-f5dc0198ff2d'

with open('berne_id_map.json', 'w') as f:
    json.dump(map, f, indent=3) 
