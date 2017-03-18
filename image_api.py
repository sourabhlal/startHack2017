import httplib, urllib, base64
import json

def search_for_image(city):
    headers = {
        # Request headers
        'Content-Type': 'multipart/form-data',
        'Ocp-Apim-Subscription-Key': '631f2ab4d4204d2fa32e8660c161a258',
    }

    params = urllib.urlencode({
        # Request parameters
        'q': city+"city",
        'count': '1',
        'offset': '0',
        'mkt': 'en-us',
        'safeSearch': 'Moderate',
    })
    data = ""
    try:
        conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v5.0/images/search?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        js = json.loads(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    return js["value"][0]["contentUrl"]

print(search_for_image("bielefeld"))