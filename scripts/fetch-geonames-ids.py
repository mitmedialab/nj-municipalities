import logging, csv, json, sys, time, re, ConfigParser, os
import requests

import cache

SETTINGS_FILE_NAME = "settings.cfg"

NJ_MUNICIPALITY_FILE = "nj-municipalities-wikipedia.csv"

GEONAMES_SEARCH_API_URL =  "http://api.geonames.org/search"
GEONAMES_NJ_ADM1 = "NJ"

scripts_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(scripts_dir),'data')
cache.set_dir(os.path.join(scripts_dir,cache.DEFAULT_DIR)) # cache the Geonames query results so we don't use up our API username tokens

# set up logging
logging.basicConfig(level=logging.INFO)
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
    'first': 0,
    'not_first': 0
}

data = []

# run through the municipalities
with open(os.path.join(scripts_dir,NJ_MUNICIPALITY_FILE), 'rb') as csvfile:
    reader = csv.reader(csvfile)
    reader.next()
    for row in reader:
        # query geonames to find matching records
        name = row[4]+" of "+row[1] # lookup as "blah of blah" seemed to work better
        name = re.sub(r'\[[^\]]*\]', '', name)  # remove footnotes, which are in square brackets
        log.info("  Investigating %s" % name)
        municipality_info = {
            'name': row[1],
            'county': row[2],
            'population2010': row[3],
            'type': row[4],
            'government': row[5],
            'geonamesId': ''
        }
        if not cache.contains(name):
            params = {
                'name': name,
                'adminCode1': GEONAMES_NJ_ADM1,
                'featureClass': 'A',
                'featureCode': 'ADMD',
                'type': 'json',
                'maxRows': '10',
                'username': geonames_username
            }
            r = requests.get(GEONAMES_SEARCH_API_URL, params=params)
            log.debug("    added to cache from %s" % r.url)
            cache.put(name,r.text)
        response_text = cache.get(name)
        results = json.loads(response_text)
        # pick the best match
        if results['totalResultsCount']>0:
            candidate = results['geonames'][0]
            if candidate['countryCode']=='US' and candidate['adminCode1']=='NJ' and candidate['fcode']=='ADMD':
                match_results['first'] = match_results['first'] + 1
                municipality_info['geonamesId'] = candidate['geonameId'];
                log.debug("    Match to geoname %d" % candidate['geonameId'])
            else:
                match_results['not_first'] = match_results['not_first'] + 1
                log.warn("  %s: First candidate doesn't match (out of %d)" % (name,results['totalResultsCount']))
        else:
            match_results['none'] = match_results['none'] + 1
            log.error("  %s: No matches :-(" % name)
        data.append( municipality_info )

# write the output CSV
with open(os.path.join(data_dir,'nj-municipalities.csv'), 'wb') as csvfile:
    writer = csv.writer(csvfile)
    columns = ['name','county','population2010','type','government','geonamesId']
    writer.writerow(columns)
    for row in data:
        info = [ row[col] for col in columns]
        writer.writerow(info)

log.info("Finished (%d total municipalities):" % len(data))
log.info("  Found %d exact matches in the first result" % match_results['first'])
log.info("  Missed %d because the first result didn't match" % match_results['not_first'])
log.info("  Missed %d because we got no results" % match_results['none'])

