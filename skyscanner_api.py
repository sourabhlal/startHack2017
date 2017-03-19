import functools
import os
import random
from pprint import pprint as pp

from dateutil import parser
from skyscanner.skyscanner import Transport, FlightsCache, Hotels
import requests as r

API_KEY = os.environ['SKYSCANNER_KEY']


###


@functools.lru_cache(maxsize=1024)
def city_string_to_id(city_as_str):
    transport_service = Transport(API_KEY)
    city_suggestion_results = transport_service.location_autosuggest(**{
        'market': 'ES',
        'currency': 'EUR',
        'locale': 'en-GB',
        'query': city_as_str
    }).json()['Places']
    if not city_suggestion_results:
        return None
    else:
        return city_suggestion_results[0]['PlaceId']


@functools.lru_cache(maxsize=1024)
def city_string_to_id_for_hotels(city_as_str):
    hotels_service = Hotels(API_KEY)
    city_suggestion_results = hotels_service.location_autosuggest(**{
        'market': 'TR',
        'currency': 'EUR',
        'locale': 'en-GB',
        'query': city_as_str
    }).json()['results']
    cities = list(filter(lambda x: x['geo_type'] == 'City', city_suggestion_results))

    if not cities:
        return None
    else:
        return cities[0]


def get_cached_offers(from_city, go_date, inbound_date):
    flights_service = FlightsCache(API_KEY)
    from_city_id = city_string_to_id(from_city)

    if not from_city_id:
        return None

    flight_resp = flights_service.get_cheapest_price_by_route(**{
        'market': 'CH',
        'currency': 'EUR',
        'locale': 'en-GB',
        # 'country': 'ES',
        'originplace': from_city_id,
        'destinationplace': 'anywhere',
        'outbounddate': go_date,
        'inbounddate': inbound_date,
        # 'adults': 1,
        # 'stops': 0
    })

    resp = flight_resp.json()

    carriers = dict([(carrier['CarrierId'], carrier) for carrier in resp['Carriers']])
    places = dict([(place['PlaceId'], place) for place in resp['Places']])
    quotes = resp['Quotes']

    checkin_year, checkin_month, checkin_monthday = go_date.split('-')
    checkout_year, checkout_month, checkout_monthday = inbound_date.split('-')
    ##pp(resp)
    booking_str = """http://www.booking.com/searchresults.html?checkin_month={checkin_month}&checkin_monthday={checkin_monthday}&checkin_year={checkin_year}&checkout_month={checkout_month}&checkout_monthday={checkout_monthday}&checkout_year={checkout_year}&ss_all=0""".format(**{
        'checkin_year': checkin_year,
        'checkin_month': checkin_month,
        'checkin_monthday': checkin_monthday,
        'checkout_year': checkout_year,
        'checkout_month': checkout_month,
        'checkout_monthday': checkout_monthday
    })



    """{shortApiKey}"""
    cleaned = [
        {
            'price': quote['MinPrice'],
            'go_carrier': carriers[quote['OutboundLeg']['CarrierIds'][0]]['Name'],
            'go_timestamp': quote['OutboundLeg']['DepartureDate'],
            'go_from': places[quote['OutboundLeg']['OriginId']]['CityName'] + ", " +
                       places[quote['OutboundLeg']['OriginId']]['CountryName'],
            'go_to': places[quote['OutboundLeg']['DestinationId']]['CityName'] + ", " +
                     places[quote['OutboundLeg']['DestinationId']]['CountryName'],
            'back_carrier': carriers[quote['InboundLeg']['CarrierIds'][0]]['Name'],
            'back_timestamp': quote['InboundLeg']['DepartureDate'],
            'back_from': places[quote['InboundLeg']['OriginId']]['CityName'] + ", " +
                         places[quote['InboundLeg']['OriginId']]['CountryName'],
            'back_to': places[quote['InboundLeg']['DestinationId']]['CityName'] + ", " +
                       places[quote['InboundLeg']['DestinationId']]['CountryName'],
            'link': "http://partners.api.skyscanner.net/apiservices/referral/v1.0/{country}/{currency}/{locale}/{originPlace}/{destinationPlace}/{outboundPartialDate}/{inboundPartialDate}?apiKey={shortApiKey}".format(
                **{
                    'country': 'CH',
                    'currency': 'EUR',
                    'locale': 'en-GB',
                    'originPlace': from_city_id,
                    'destinationPlace': places[quote['OutboundLeg']['DestinationId']]['SkyscannerCode'],
                    'outboundPartialDate': go_date,
                    'inboundPartialDate': inbound_date,
                    'shortApiKey':API_KEY[:16]
                }
            ),
            'booking_link': booking_str+"&ss={ss}&ss_raw={ss_raw}".format(**{'ss': places[quote['OutboundLeg']['DestinationId']]['CityName'], 'ss_raw': places[quote['OutboundLeg']['DestinationId']]['CityName']})
        } for quote in quotes if quote['OutboundLeg']['CarrierIds'] and quote['InboundLeg']['CarrierIds']
        ]

    offers = sorted(cleaned, key=lambda x: x['price'])
    return offers


def get_best_hotel(city, date_in, date_out):
    hotels_service = Hotels('prtl6749387986743898559646983194')
    city = city_string_to_id_for_hotels(city)

    resp = hotels_service.get_result(**{
        'market': 'ES',
        'currency': 'EUR',
        'locale': 'en-GB',
        'country': 'ES',
        'entityid': city['individual_id'],
        'checkindate': date_in,
        'checkoutdate': date_out,
        'guests': 1,
        'rooms': 1
    })

    hotels_prices = dict([(hotel['id'], hotel) for hotel in resp.json()['hotels_prices']])
    hotels = sorted(resp.json()['hotels'], key=lambda x: x['popularity'])
    for hotel in hotels:
        hotel['price'] = hotels_prices[hotel['hotel_id']]['agent_prices'][0]['price_total']

    if not hotels:
        return {}

    the_hotel_offer = random.choice(hotels[:5])
    return {
        'type': 'hotel',
        'date': date_out,
        'price': str(int(the_hotel_offer['price'])),
        # 'details': {
        #    'latitude': the_hotel_offer['latitude'],
        #    'longitude': the_hotel_offer['longitude'],
        #    'name': the_hotel_offer['name'],
        #    'checkin': date_in,
        #    'checkout': date_out
        # }
        'description': "In %s, stay at %s, until %s" % (
            city['display_name'], the_hotel_offer['name'], parser.parse(date_out).strftime("%B %d, %Y, %A")),
        'detailsLink': '#',
        'img': ''
    }


@functools.lru_cache(maxsize=1024)
def search_for_image(city):
    headers = {
        # Request headers
        'Content-Type': 'multipart/form-data',
        'Ocp-Apim-Subscription-Key': '631f2ab4d4204d2fa32e8660c161a258',
    }
    params = {
        # Request parameters
        'q': city  +" city",
        'count': '1',
        'offset': '0',
        'mkt': 'en-us',
        'safeSearch': 'Moderate',
    }
    resp = r.get('https://api.cognitive.microsoft.com/bing/v5.0/images/search', params=params, headers=headers)
    try:
        return resp.json()["value"][0]["contentUrl"]
    except Exception as e:
        print(resp.json())
        return ""


if __name__ == "__main__":
    pp(get_best_hotel('Barcelona', '2017-10-19', '2017-10-20'))
    # pp(get_best_flight('Barcelona', 'London', '2017-10-20'))
    # pp(get_cached_offers('Barcelona', '2017-10-20', '2017-10-25'))
    pass
