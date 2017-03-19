import base64
import concurrent.futures
import requests as r
from dateutil import parser

from bottle import run, request, Bottle, response, static_file, template, redirect
from dbapi import CLIENT_ID, SECRET_KEY, get_user_info
from skyscanner_api import get_cached_offers, search_for_image

HEADER_BASE64 = base64.b64encode((CLIENT_ID + ":" + SECRET_KEY).encode())

app = Bottle()

mainstream_cities = ["London","Bangkok","Paris","Dubai","Istanbul","New York","Singapore","Kuala Lumpur","Seoul","Hong Kong","Tokyo","Barcelona","Amsterdam","Rome","Milan","Taipei","Shanghai","Vienna","Prague","Los Angeles","Las Vegas", "Pattaya", "Miami", "Guangzhou", "Antalya", "Taipei"];


@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route('/surprise', method=['OPTIONS', 'POST'])
def flight_api():
    if request.method == 'OPTIONS':
        return {}

    # parse post body as json
    params = request.json

    if not params:
        return {'data': []}

    start_date = parser.parse(params['startDate'])
    final_date = parser.parse(params['endDate'])

    return None


@app.route('/login_redirect', method=['GET'])
def getting_fresh_token():
    params = request.query.decode()
    code = params.get('code')

    resp = r.post('https://simulator-api.db.com/gw/oidc/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:8100/login_redirect',
    }, headers={
        'Authorization': b"Basic " + HEADER_BASE64
    })

    resp_dict = resp.json()
    access_token = resp_dict.get('access_token')

    redirect('/static/results.html?%s' % access_token)


@app.route('/api/info', method=['POST'])
def info_api():
    params = request.json
    token = params.get('access_token')
    return get_user_info(token)


@app.route('/api/flights', method=['POST'])
def flights_api():
    params = request.json
    token = params.get('access_token')

    city = params.get('city')
    start_date = params.get('start')
    end_date = params.get('end')

    inter_results = get_cached_offers(city, start_date, end_date)

    target = float(params.get('target_price'))
    limit = float(params.get('limit'))
    ratio = float(params.get('ratio'))

    dist_func = lambda x: abs(x['price'] - target)
    limiter = lambda x: x['price'] <= limit * 0.8

    non_hipster = list(filter(lambda x: x["go_to"].split(",")[0] in mainstream_cities, inter_results))
    hipster = list(filter(lambda x: x["go_to"].split(",")[0] not in mainstream_cities, inter_results))

    final = list(
        sorted(
            filter(limiter, non_hipster), key=dist_func
        )
    )[:int(ratio)] + list(
        sorted(
            filter(limiter, hipster), key=dist_func
        )
    )[:9-int(ratio)]



    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        final_2 = executor.map(
            lambda x: {**x, 'background': search_for_image(x['go_to'].split(',')[0].strip().lower()), 'is_mainstream': x['go_to'].split(',')[0].strip() in mainstream_cities}, final
        )

    return {
        'result': list(final_2)
    }


@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./frontend/')


if __name__ == '__main__':
    run(app, host='localhost', port=8100)
