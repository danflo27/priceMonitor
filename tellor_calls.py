from web3 import Web3
import helpers as h
import time
import random
import sys

etherscan_api_url = "https://api.etherscan.io/api"
btc_query_id = 'a6f013ee236804827b77696d350e9f0ac3e879328f2a3021d473a0b778ad78ac'
eth_query_id = '83a7f3d48786ac2667503a61e8c415438ed2922eb86a2906e4ee66d9a2ce4992'
ids = [bytes.fromhex(eth_query_id), bytes.fromhex(btc_query_id)]

def web3_connect(infura_url):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    return w3

def create_contract(add, abi, w3):
    return w3.eth.contract(address = add, abi = abi)

# Finds the number of reports for a given queryId, gets the timestamp for each of those reports, 
# and then grabs the value reported for each of those reports.
def get_data_before(id, contract, num_reports):
    values_by_timestamp = {}
    timestamps = []
    spinner = ['-', '\\', '|', '/']
    spinner_length = len(spinner)
    new_value_count = tellor_get_new_value_count_by_queryId(id, contract)
    for i in range(new_value_count - 1, max(new_value_count - num_reports - 1, -1), -1):
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
        sys.stdout.write(spinner[i % spinner_length])  # Print the next spinner character
        sys.stdout.flush()  # Ensure the character is displayed
        time.sleep(random.uniform(0.0, 0.2))
        tellor_timestamp = tellor_get_timestamp_by_queryId_and_index(id, i, contract)
        timestamps.append(tellor_timestamp)
        get_data_before_response  = tellor_get_data_before(id, (tellor_timestamp + 1), contract)
        value =  (int.from_bytes(get_data_before_response[1], byteorder='big')/1e18).__round__(2)
        values_by_timestamp[tellor_timestamp] = value
        sys.stdout.write('\b')
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()
    average_time_difference = h.get_avg_time_between_reports(timestamps)
    return values_by_timestamp, average_time_difference

def tellor_get_new_value_count_by_queryId(queryId, contract):
    new_value_count = contract.functions.getNewValueCountbyQueryId(queryId).call()
    return new_value_count

def tellor_get_timestamp_by_queryId_and_index(queryId, index, contract):
    timestamp = contract.functions.getTimestampbyQueryIdandIndex(queryId, index).call()
    return timestamp

def tellor_get_data_before(id, timestamp, contract):
    data = contract.functions.getDataBefore(id, timestamp).call()
    return data