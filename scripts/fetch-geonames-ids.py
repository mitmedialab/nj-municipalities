import logging, json, sys, time, re, ConfigParser, os
import requests, csvkit

import cache

SETTINGS_FILE_NAME = "settings.cfg"

NJ_MUNICIPALITY_FILE = "nj-municipalities-wikipedia.csv"

GEONAMES_SEARCH_API_URL =  "http://api.geonames.org/search"
GEONAMES_NJ_ADM1 = "NJ"

scripts_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(scripts_dir),'data')
cache.set_dir(os.path.join(scripts_dir,cache.DEFAULT_DIR)) # cache the Geonames query results so we don't use up our API username tokens

# set up logging
logging.basicConfig(level=logging.WARN)
log = logging.getLogger(__name__)
start_time = time.time()
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARN)

# load the settings
log.info("Loading settings from %s" % SETTINGS_FILE_NAME)
settings = ConfigParser.ConfigParser()
settings_file_path = os.path.join(scripts_dir, SETTINGS_FILE_NAME)
settings.read(settings_file_path)

geonames_username = settings.get('geonames','username')
if geonames_username=='demo':
    log.error("Sign up for a Geonames username and enter it in the scripts/settings.cfg file")
    sys.exit()

# start the scraping process

log.info("Loading municipality list from %s" % NJ_MUNICIPALITY_FILE)

match_results = { # track results
    'none': 0,
    'found': 0,
    'no_match': 0,
    'duplicate_match': 0
}

geonames_picked_already = {}
data = []

def _pick_best_match(results,name,municipality_info,check_against_name):
    for candidate in results['geonames']:
        log.debug("    compare to %d: %s" % (candidate['geonameId'],candidate['name']) )
        if candidate['countryCode']=='US' and candidate['adminCode1']=='NJ' \
            and ( (check_against_name is False) or (name==candidate['name']) ) \
            and candidate['fcode']=='ADMD' and (municipality_info['county'] in candidate['adminName2']):
                return candidate
    return None

# run through the municipalities
with open(os.path.join(scripts_dir,NJ_MUNICIPALITY_FILE), 'rb') as csvfile:
    reader = csvkit.reader(csvfile)
    reader.next()
    for row in reader:
        # query geonames to find matching records
        name = row[4]+" of "+row[1] # lookup as "blah of blah" seemed to work better
        name = re.sub(r'\[[^\]]*\]', '', name)  # remove footnotes, which are in square brackets
        municipality_info = {
            'name': row[1],
            'county': row[2],
            'population2010': row[3].replace(",",""),
            'type': row[4],
            'government': row[5],
            'geonamesId': ''
        }
        log.info("  Investigating %s in %s as '%s'" % (municipality_info['name'],municipality_info['county'],name) )
        if not cache.contains(name):
            params = {
                'name': name,
                'adminCode1': GEONAMES_NJ_ADM1,
                'featureClass': 'A',
                'featureCode': 'ADMD',
                'type': 'json',
                'maxRows': '10',
                'username': geonames_username,
                'style': 'full'
            }
            r = requests.get(GEONAMES_SEARCH_API_URL, params=params)
            log.debug("    added to cache from %s" % r.url)
            cache.put(name,r.text)
        results = json.loads( cache.get(name) )
        # pick the best match
        if results['totalResultsCount']>0:
            match = _pick_best_match(results,name,municipality_info,True)
            if match is None:
                match = _pick_best_match(results,name,municipality_info,False)
            if match is not None:
                if match['geonameId'] in geonames_picked_already:
                    log.error("    Matched to geoname %d, but we've picked that already for %s in %s:-(" % 
                        (match['geonameId'],
                            geonames_picked_already[match['geonameId']]['name'],
                            geonames_picked_already[match['geonameId']]['county']) )
                    match_results['duplicate_match'] = match_results['duplicate_match'] + 1
                else:
                    geonames_picked_already[match['geonameId']] = municipality_info
                    match_results['found'] = match_results['found'] + 1
                    municipality_info['geonamesId'] = match['geonameId']
                    log.debug("    Match to geoname %d" % match['geonameId'])
            else:
                match_results['no_match'] = match_results['no_match'] + 1
                log.error("  %s: didn't find a match in the results (county of %s)" % (name,municipality_info['county']))
        else:
            match_results['none'] = match_results['none'] + 1
            log.error("  %s: No matches :-(" % name)
        data.append( municipality_info )

# write the output CSV
with open(os.path.join(data_dir,'nj-municipalities.csv'), 'wb') as csvfile:
    writer = csvkit.writer(csvfile)
    columns = ['name','county','population2010','type','government','geonamesId']
    writer.writerow(columns)
    for row in data:
        info = [ row[col] for col in columns]
        writer.writerow(info)

log.info("Finished (%d total municipalities):" % len(data))
log.info("  Found %d matches" % match_results['found'])
log.info("  Missed %d because we matched to one we already used" % match_results['duplicate_match'])
log.info("  Missed %d because we couldn't find a match in the results" % match_results['no_match'])
log.info("  Missed %d because we got no results" % match_results['none'])

