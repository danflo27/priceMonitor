import tellor_calls as tellor 
import dune_queries as dune
import json
from dotenv import load_dotenv
import os
import helpers as h
import art

# load api keys
load_dotenv('./data/data.env')
infura_link = os.getenv('INFURA_PROJECT_URL')
dune_api_key = os.getenv('DUNE_API_KEY')

# get dune price data
# data comes from coinpaprika api https://docs.dune.com/data-catalog/spellbook/top-tables/prices#pricesusd
btc_dune_data = dune.get_dune_btc_data(dune_api_key)
eth_dune_data = dune.get_dune_eth_data(dune_api_key)
for item in btc_dune_data:
    item['interval_start'] = h.to_unix_time(item['interval_start'])
for item in eth_dune_data:
    item['interval_start'] = h.to_unix_time(item['interval_start'])

# get usingtellor abi and address
with open('./data/ext_data.json') as f:
    data = json.load(f)
tellor_dict = data['tellor']

btc_query_id = bytes.fromhex('a6f013ee236804827b77696d350e9f0ac3e879328f2a3021d473a0b778ad78ac')
eth_query_id = bytes.fromhex('83a7f3d48786ac2667503a61e8c415438ed2922eb86a2906e4ee66d9a2ce4992')
query_ids = [btc_query_id, eth_query_id]
eth_dict, btc_dict = {}, {}
eth_data_points, btc_data_points = [], []
keys = ["dune price", "dune timestamp", "reported price", "reported timestamp", "difference", "absolute difference", "absolute percent diff"]

def create_report(data_points, symbol):
    total_abs_diff, total_diff, total_abs_percent_diff = 0, 0, 0
    length = len(data_points)
    for item in data_points:
        total_abs_diff += item["absolute difference"]
        total_diff += item["difference"]
        total_abs_percent_diff += item["absolute percent diff"]
    
    avg_abs_diff =(total_abs_diff/length).__round__(2)
    print ("average absolute difference: $" + str(avg_abs_diff))
    avg_diff = (total_diff/length).__round__(2)
    print ("average difference: $" + str(avg_diff) )
    avg_abs_percent_diff = (total_abs_percent_diff/ length).__round__(2)
    print ("average absolute percent difference: " + str(avg_abs_percent_diff) + "%")
    max_diff = h.find_max_difference(data_points)
    print ("max difference: " + str(max_diff) + "\n")

    h.plot_differences(data_points, symbol)
    
    return avg_abs_diff, avg_diff, avg_abs_percent_diff, max_diff

def get_report_data(query_ids, num_reports):
    symbol = None
    for query_id in query_ids:  # Iterate through each query ID
        if query_id == btc_query_id:
            symbol = "BTC"
            symbol_art = art.text2art(symbol)
            print(symbol_art)
            print("Getting the last " + str(num_reports) + " BTC reports ", end="")
            dune_data = btc_dune_data
        elif query_id == eth_query_id:
            symbol = "ETH"
            symbol_art = art.text2art(symbol)
            print(symbol_art)
            print("Getting the last " + str(num_reports) + " ETH reports ", end="")
            dune_data = eth_dune_data

        w3 = tellor.web3_connect(infura_link)
        tellor_con = tellor.create_contract(tellor_dict['address'], tellor_dict['abi'], w3)
        tellor_data, average_time_difference = tellor.get_data_before(query_id, tellor_con, num_reports)
        avg_time_difference_in_min = (average_time_difference / 60).__round__(1)

        data_points = []
        for key in tellor_data:
            for item in dune_data:
                timestamp_diff = (key - item['interval_start'])
                if 0 < timestamp_diff < 60:
                    data_dict = dict.fromkeys(keys, None)
                    data_dict["dune price"] = item['avg_price']
                    data_dict["dune timestamp"] = item['interval_start']
                    data_dict["reported price"] = tellor_data[key]
                    data_dict["reported timestamp"] = key
                    data_dict["difference"] = float(tellor_data[key]) - float(item['avg_price'])
                    data_dict["absolute difference"] = abs(float(tellor_data[key]) - float(item['avg_price']))
                    data_dict["absolute percent diff"] = ((abs(float(tellor_data[key]) - float(item['avg_price'])) / float(item['avg_price'])) * 100).__round__(4)
                    data_points.append(data_dict)
        num_reports_included = len(data_points)
        if num_reports_included < 0.8*num_reports:
            print ("\n ** the number of reports matching dune's historical market data is less than 80%. consider re-running the dune query **")
        print ("\nnumber of reports included: " + str(num_reports_included))
        print ("average # of min between reports: " + str(avg_time_difference_in_min) + " min")
        create_report(data_points, symbol)
        print ("-" * 20)
    return data_points, average_time_difference, symbol



get_report_data(query_ids, 400)