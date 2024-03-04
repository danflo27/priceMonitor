import requests

def get_dune_eth_data(dune_api_key):
    dune_eth_query_id = '3475754'
    headers = {"X-DUNE-API-KEY": dune_api_key}
    eth_url = "https://api.dune.com/api/v1/query/" + dune_eth_query_id + "/results"

    dune_eth_response = requests.request("GET", eth_url, headers=headers)
    eth_dune_query = dune_eth_response.json()
    eth_dune_query = eth_dune_query['result']['rows']
    return eth_dune_query

def get_dune_btc_data(dune_api_key):
    dune_btc_query_id = '3461050'
    headers = {"X-DUNE-API-KEY": dune_api_key}
    btc_url = "https://api.dune.com/api/v1/query/" + dune_btc_query_id + "/results"

    dune_btc_response = requests.request("GET", btc_url, headers=headers)
    btc_dune_query = dune_btc_response.json()
    btc_dune_query = btc_dune_query['result']['rows']
    return btc_dune_query



