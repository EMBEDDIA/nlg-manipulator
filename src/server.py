from service import ElectionNlgService
import os
import random
import sys
import argparse
from bottle import Bottle, route, request, response, run, redirect, view, TEMPLATE_PATH, static_file, get, post

#
# START INIT
#

# CLI parameters
parser = argparse.ArgumentParser(description='Run the Valtteri server.')
parser.add_argument('port', type=int, default=8080, help='port number to attach to')
parser.add_argument('--force-cache-refresh', action='store_true', default=False, help="re-compute all local caches")
parser.add_argument('--redis', action='store_true', default=False, help="use Redis to cache generated content (assumes REDISCLOUD_URL is set in ENV)")
args = parser.parse_args()
sys.argv = sys.argv[0:1]

# Logging
import logging
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log = logging.getLogger('root')
log.setLevel(logging.ERROR)
log.addHandler(handler)

# Redis
if args.redis:
    import urllib.parse
    import redis
    url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
    cache = redis.Redis(host=url.hostname, port=url.port, password=url.password)
    #cache.flushdb()

# Bottle
app = Bottle()
service = ElectionNlgService(
    random_seed = 4551546,
    force_cache_refresh = args.force_cache_refresh
)
TEMPLATE_PATH.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/../views/")
static_root = os.path.dirname(os.path.realpath(__file__)) + "/../static/"

#
# END INIT
#

def allow_cors(func):
    """ this is a decorator which enable CORS for specified endpoint """
    def wrapper(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return func(*args, **kwargs)
    return wrapper

def get_article(language, where, where_type):
    if not args.redis:
        log.info("Redis is not enabled, starting pipeline")
        headline, body = service.run_pipeline(language, where, where_type)
        return headline, body
    else:
        key = "{}|{}|{}|{}|{}".format(language, where, where_type)
        cached = cache.get(key)
        if not cached:
            log.info("Key was not in Redis, updating cache")
            headline, body = service.run_pipeline(language, where, where_type)
            value = "{}|SPLIT|{}".format(headline, body)
            cache.set(key, value)
            return headline, body
        else:
            log.info("Found key in Redis")
            cached = cached.decode('utf-8')
            parts = cached.split("|SPLIT|")
            if len(parts) != 2:
                log.debug("Invalid value in Redis. Clearing cache and trying again.")
                cache.flushdb()
                return get_article(language, where, where_type)
            return parts[0], parts[1]

@app.route('/')
@view('index')
def index():
    return {}

@app.route('/tietosuoja')
@view('tietosuoja')
def tietosuoja():
    return {}

@app.post('/news')
def news_html_search():
    language = request.forms.get('language')
    if not language:
        language = "fi"

    location = request.forms.get('location')
    if not location:
        where_type = 'C'
        where = 'fi'
    else:
        where_type = location[0]
        where = location[1:]
    
    redirect('/news?language={}&where={}&where_type={}'.format(language, where, where_type))

@app.get('/city')
def geolocate():
    language = request.query.language or "fi"

    city = request.query.city or None
    if not city:
        redirect('/')

    code = service.get_city_code(city)
    if not code:
        redirect('/')

    redirect('/news?language={}&where={}&where_type=M'.format(language, code))


@app.get('/news')
@view('news-article')
def news_html():
    language = request.query.language or "fi"
    where = request.query.where or None
    where_type = request.query.where_type or None

    if not where:
        redirect('/')

    if not where:
        where_type = 'C'
        where = 'fi'

    header, body = get_article(language, where, where_type)
    return dict({
        "where": where,
        "where_type": where_type,
        "language": language,
        "header": header,
        "body": body,
    })


@app.route('/api/news')
@allow_cors
def news_api():
    language = request.query.language or "fi"
    where = request.query.where or None
    where_type = request.query.where_type or None

    if not where:
        response.status = 400
        return {"error": "Must have at least one of the following query parameters: 'where'"}

    if not where:
        where_type = 'C'
        where = 'fi'

    header, body = get_article(language, where, where_type)
    return dict({
        "where": where,
        "where_type": where_type,
        "language": language,
        "header": header,
        "body": body,
    })

def random_news():
    language = request.query.language or "fi"
    geodata = service.registry.get('geodata-lookup')
    options = list(geodata.get(language, geodata["fi"])["M"].keys())
    m = random.choice(options)

    header, body = get_article(language, None, None, m, "M")
    return dict({
        "where": m,
        "where_type": "M",
        "language": language,
        "header": header,
        "body": body,
    })

@app.route('/random')
@view('news-article')
def random_news_html():
    return random_news()

@app.route('/api/random')
@allow_cors
def random_news_api():
    return random_news()

@app.route('/static/<filename:path>')
@allow_cors
def serve_static(filename="index.html"):
    return static_file(filename, root=static_root)

@app.route('/api/geodata')
@allow_cors
def get_geodata():
    language = request.query.language or "fi"
    return {"data": service.get_geodata(language)}

@app.route('/api/entities')
@allow_cors
def get_entities():
    language = request.query.language or "fi"
    location = request.query.l or None
    return service.get_entities(language, location)

@app.route('/api/languages')
@allow_cors
def get_languages():
    return {"languages": ["fi", "sv", "en"]}

@app.route('/api/headlines')
@allow_cors
def get_random_headlines():
    language = request.query.language or "fi"
    if not args.redis:
        return {
            "headlines": []
        }
    else:
        headlines = []
        for i in range(50):
            key = cache.randomkey()
            if not key:
                return {"headlines": []}
            key = key.decode('utf-8')
            if not key.startswith(language):
                continue

            value = cache.get(key)
            if not value:
                continue
            value = value.decode('utf-8')
            
            parts = key.split("|")
            headline = {
                "language": None if parts[0] == "None" else parts[0],
                "where": None if parts[3] == "None" else parts[3],
                "where_type": None if parts[4] == "None" else parts[4],
                "headline": value.split("|SPLIT|")[0]
            }
            if not headline in headlines:
                headlines.append(headline)
            if len(headlines) >= 4:
                return {"headlines": headlines} 

        return {"headlines": headlines}

def main():
    log.info("Starting with options port={}, redis={}".format(args.port, args.redis))
    run(app, server='meinheld', host='0.0.0.0', port=args.port)
    log.info("Stopping")

if __name__ == '__main__':
    main()
