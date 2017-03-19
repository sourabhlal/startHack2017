from pprint import pprint as pp

import functools
import requests


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


CLIENT_ID = '75ba6ea7-2a19-401b-a982-50aed2d858da'
SECRET_KEY = 'AL09rGMifhoHArDiMuX6zLIwtuWrrFT1a0DeuREl57EWVXIG_lHhhfGROhKx_YtnnD0lIxW1vSgRJMs5ICMaru8'

TRANS_ENDPOINT = 'https://simulator-api.db.com/gw/dbapi/v1/transactions'
ADDR_ENDPOINT = 'https://simulator-api.db.com/gw/dbapi/v1/addresses'
USER_INFO = 'https://simulator-api.db.com/gw/dbapi/v1/userInfo'
CASH_ACCOUNTS = 'https://simulator-api.db.com/gw/dbapi/v1/cashAccounts'

access_token = ""


def get_address(address_list):
    valids = list(filter(lambda x: x['type'] == 'REGISTRATION_ADDRESS', address_list))
    if valids:
        print(valids[0])
        return valids[0]['city']#+", "+valids[0]['country']
    return None

@functools.lru_cache(maxsize=1024)
def get_user_info(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    r_info = requests.get(USER_INFO, headers=headers).json()
    accounts = requests.get(CASH_ACCOUNTS, headers=headers).json()
    print(accounts)
    r_account = sorted(accounts, key=lambda x: x['balance'])[-1]
    r_address = get_address(requests.get(ADDR_ENDPOINT, headers=headers).json())


    previous_avg_cost, trips = get_previous_avg_cost(access_token)
    return {
        "info": r_info,
        "account": r_account,
        "address": r_address,
        "previous_avg": -previous_avg_cost,
        "trips": trips
    }


def _process_transaction(transaction):
    if 'Deutsche Bahn AG' in transaction['counterPartyName']:
        return {
            "type": "train",
            "travel": list(map(lambda x: x.strip().rstrip('HBF').strip(), transaction['usage'].split('Ticket')[1].split('-'))),
            "date": transaction['bookingDate']
        }
    elif 'AIRLINE' in transaction['counterPartyName']:
        return {
            "type": "plane",
            "travel": list(map(lambda x: x.strip(), transaction['usage'].split('-'))),
            "date": transaction['bookingDate']
        }

def get_previous_avg_cost(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    r = requests.get(TRANS_ENDPOINT, headers=headers)
    resp = r.json()

    trip_transcations = [
        (idx, _process_transaction(trans))
        for idx, trans in enumerate(resp) if 'Deutsche Bahn AG' in trans['counterPartyName'] or "AIRLINE" in trans['counterPartyName']
        ]

    total_trans_amount = 0.0

    for start, end in pairwise(trip_transcations):
        start_idx, _ = start
        end_idx, _ = end
        total_trans_amount += sum(
            map(lambda x: min(x['amount'], 0), resp[start_idx:end_idx + 1])
        )

    trips = [
        {
            "go": end[1],
            "back": start[1],
            "type": start[1]["type"]
        } for start, end in pairwise(trip_transcations)
    ]
    return total_trans_amount / (len(trip_transcations) / 2), trips[:2]

if __name__ == "__main__":
    r = requests.get(TRANS_ENDPOINT, headers=headers)

    resp = r.json()

    trip_transcations = [
        (idx, list(map(lambda x: x.rstrip(' HBF'), trans['usage'].split('Ticket')[1].split(' - '))))
        for idx, trans in enumerate(resp) if 'Deutsche Bahn' in trans['counterPartyName']
        ]

    pp(trip_transcations)

    r = requests.get(ADDR_ENDPOINT, headers=headers)

    total_trans_amount = 0.0

    for start, end in pairwise(trip_transcations):
        start_idx, _ = start
        end_idx, _ = end
        total_trans_amount += sum(
            map(lambda x: min(x['amount'], 0), resp[start_idx:end_idx + 1])
        )

    avg_amount = total_trans_amount / (len(trip_transcations) / 2)

    print(avg_amount)
