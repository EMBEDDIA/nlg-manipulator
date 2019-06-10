from service import CrimeNlgService
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
args = parser.parse_args()
sys.argv = sys.argv[0:1]

# Logging
import logging
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log = logging.getLogger('root')
log.setLevel(logging.INFO)
#log.setLevel(5) # Enable for way too much logging, even more than DEBUG
log.addHandler(handler)

# Bottle
app = Bottle()
service = CrimeNlgService(
    random_seed = 4551546,
    force_cache_refresh = args.force_cache_refresh, nomorphi=False
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
    return service.run_pipeline(language, where, where_type)

@app.route('/')
@view('index')
def index():
    return {}

@app.route('/tietosuoja')
@view('tietosuoja')
def tietosuoja():
    return {}

@app.get('/api')
@allow_cors
def api_index():
    redirect('/api/random')

@app.get('/api/')
@allow_cors
def api_index_slash():
    redirect('/api/random')

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

@app.get('/news/')
def news_html_slash():
    redirect('/news')

@app.get('/news')
@view('news-article')
def news_html():
    language = request.query.language or "fi"
    where = request.query.where or None
    where_type = request.query.where_type or None

    if not where:
        where_type = 'C'
        where = 'fi'

    header, body, locator_map, graph = get_article(language, where, where_type)
    return dict({
        "where": where,
        "where_type": where_type,
        "language": language,
        "header": header,
        "body": body,
        "locator_map": locator_map,
        "graph": graph
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

    header, body, locator_map, graph = get_article(language, where, where_type)
    return dict({
        "where": where,
        "where_type": where_type,
        "language": language,
        "header": header,
        "body": body,
        "locator_map": locator_map,
        "graph": graph,
    })

def random_news():
    language = request.query.language or "fi"
    geodata = service.registry.get('geodata-lookup')
    options = list(geodata.get(language, geodata["fi"])["M"].keys())
    m = random.choice(options)

    header, body, locator_map, graph = get_article(language, m, "M")
    return dict({
        "where": m,
        "where_type": "M",
        "language": language,
        "header": header,
        "body": body,
        "locator_map": locator_map,
        "graph": graph,
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

@app.route('/api/languages')
@allow_cors
def get_languages():
    return {"languages": ["fi", "en"]}

@app.route('/api/geodata')
@allow_cors
def get_geodata():
    language = request.query.language or "fi"
    return {"data": service.get_geodata(language)}

def main():
    log.info("Starting with options port={}".format(args.port))
    run(app, server='meinheld', host='0.0.0.0', port=args.port)
    log.info("Stopping")

if __name__ == '__main__':
    main()
