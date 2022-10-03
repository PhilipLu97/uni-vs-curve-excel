from urllib.error import HTTPError
from enum import Enum
import xlwings as xw
import pandas as pd 
import requests
import datetime
import math
    
# Use DeFiLlama API for tvl data
tvl_endpoint = 'https://api.llama.fi/tvl/{id}' 

# Use CoinGecko API for token data like price, market cap, etc.
token_endpoint = 'https://api.coingecko.com/api/v3/coins/{id}' 
    
# IDs of protocols in DeFiLlama API
llama_ids = ['uniswap', 'curve']

# IDs of dapp coins in CoinGecko API
gecko_ids = ['uniswap', 'curve-dao-token']

# Names of rows that I want to appear in the Excel table, in order (some require API calls and computation)
# note: The API landscape is inconsistent, so finding some of this data, like the time series for DEX volume,
# would be too time-consuming, so I'm ditching this idea
'''
metrics = ['TVL (USD)', 'TVL (ETH)', 'Market Cap (USD)', '6-Month Weekly Average Volume (USD)', 
            '6-Month Weekly Average Volume (ETH)', 'Market Share (TVL)', 'Market Share (Volume)', 
            'Market Share (Rewards)', "Integrations Cumulative Market Cap"]
'''

# IDs of integrated DeFi apps in CoinGecko API - only want Market Cap Data
# note: Market cap data is inconsistent as some coins have unknown circulating supply,
# so that's why I'm deciding to not use this metric
# defi_integrations = {'uniswap':['aave', '1inch', 'gelato', ], 'curve':['y']}

# Currencies to denominate metrics in
# Crypto assets are generally higher correlated with ETH than with the USD 
class Denomination(Enum):
    USD = 1
    ETH = 2 

def main():
    #xlwings stuff that lets Python output to an Excel spreadsheet
    wb = xw.Book.caller()
    sheet = wb.sheets[0]
    
    '''
    Tests
    
    print(cumulativeMarketCaps(['curve-dao-token', 'uniswap', 'aave'], Denomination.ETH))
    print(getTvl('uniswap', Denomination.USD))
    print(getTvl('uniswap', Denomination.ETH))
    print(getMarketCap('pancakeswap-token', Denomination.USD))
    '''
    
    tvls_usd = [0, 0]
    tvls_eth = [0, 0]
    marketcaps_usd = [0, 0] 
    marketcaps_eth = [0, 0]
    
    for index, dapp in enumerate(llama_ids):
        tvls_usd[index] = getTvl(dapp, Denomination.USD)
        
    for index, dapp in enumerate(llama_ids):
        tvls_eth[index] = getTvl(dapp, Denomination.ETH)
        
    for index, dapp in enumerate(gecko_ids):
        marketcaps_usd[index] = getMarketCap(dapp, Denomination.USD)
        
    for index, dapp in enumerate(gecko_ids):
        marketcaps_eth[index] = getMarketCap(dapp, Denomination.ETH)
    
    df = pd.DataFrame([tvls_usd, tvls_eth, marketcaps_usd, marketcaps_eth], columns=llama_ids)
    #sheet.range('A11').options(index=False).value = df
    sheet.range('B1').options(index=False, header=False).value = df
    
# Get the cumulative market caps of an array of protocols in USD from CoinGecko API
# getMarketCaps: list[Str] -> Str

def cumulativeMarketCaps(protocols: list[str], currency: Denomination):
    cumulative_mc = 0
    
    for dapp in protocols:
        cumulative_mc += getMarketCapNumber(dapp, currency)
    
    if currency == Denomination.USD:
        cumulative_mc = '${:,}'.format(cumulative_mc)
    elif currency == Denomination.ETH:
        cumulative_mc = '{:,} ETH'.format(cumulative_mc)
        
    return cumulative_mc

# Get the market cap of a protocol in USD from CoinGecko API
# getMarketCaps: Str Denomination -> Str

def getMarketCap(dapp: str, currency: Denomination):
    mc = getMarketCapNumber(dapp, currency)
    
    if currency == Denomination.USD:
        mc = '${:,}'.format(mc)
    elif currency == Denomination.ETH:
        mc = '{:,} ETH'.format(mc)
    
    return mc

# Helper function for the other market cap functions. Returns only an Integer market cap value
# getMarketCaps: Str Denomination -> Int

def getMarketCapNumber(dapp: str, currency: Denomination):
    try:
        response = requests.get(
            token_endpoint.format(id = dapp),
            params={'community_data':'false', 'developer_data':'false'},
            headers={'accept': 'application/json'},
        )
            
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise http_err
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise err
    else:
        if currency == Denomination.USD:
            mc = response.json()["market_data"]["market_cap"]["usd"]
        elif currency == Denomination.ETH:
            mc = response.json()["market_data"]["market_cap"]["eth"]
    
    return mc

# Get the TVL of a dapp in either USD or ETH from DeFiLlama API
# getTvl: Str Denomination -> Str

def getTvl(dapp: str, currency: Denomination):
    tvl = getTvlNumber(dapp, currency)
    
    if currency == Denomination.USD:
        tvl = '${:,}'.format(tvl)
    elif currency == Denomination.ETH:
        tvl = '{:,} ETH'.format(tvl)
    
    return tvl

# Helper function for getTvl that returns an Integer TVL value of a dapp
# getTvl: Str Denomination -> Int

def getTvlNumber(dapp: str, currency: Denomination):
    try:
        response = requests.get(
            tvl_endpoint.format(id = dapp),
            params={},
            headers={},
        )
        
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise http_err
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise err
    else:
        # DeFiLlama API returns TVL in USD only
        tvl = response.json()
        
    if currency == Denomination.USD:
        tvl = math.floor(tvl)
    elif currency == Denomination.ETH:
        tvl = math.floor(tvl / getPrice('ethereum'))
        
    return tvl
    
# Get the price of a token in USD from CoinGecko API. For best results, type out the full name (i.e, "bitcoin")
# getPrice: Str -> Float

def getPrice(token: str):
    try:
        response = requests.get(
            token_endpoint.format(id = token),
            params={},
            headers={},
        )
        
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise http_err
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise err
    else:
        price = response.json()['market_data']['current_price']['usd']
        
    return price

if __name__ == "__main__":
    xw.Book("uni_vs_curve_metrics.xlsm").set_mock_caller()
    main()
