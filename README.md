# uni-vs-curve-excel
This mini-project lets you make requests to [CoinGecko](https://www.coingecko.com/en/api/documentation) and [DefiLlama](https://defillama.com/docs/api) APIs for market cap and TVL figures for both Uniswap and Curve denominated in either USD or ETH. Valid responses are inserted into a [pandas](https://pandas.pydata.org/) dataframe and then output to Excel using the [xlwings](https://www.xlwings.org/) library. You can extend this project to get market cap/TVL data for other DeFi protocols as well.

NOTE: **Excel macros must be enabled** for this project to work, so if you are uncomfortable with turning them on, go no further. 

## Setup

### Dependencies
```
xlwings
pandas
```
### Steps
1. With Python 3 installed, install the dependencies using pip. 
2. pandas likely won't require any extra setup, but xlwings will: follow this [guide](https://towardsdatascience.com/how-to-supercharge-excel-with-python-726b0f8e22c2) until you've read through the "Getting Started with xlwings" section to enable xlwings to work with Excel. The .bas file in this repository required to run Python from Excel is the same as the default one created by xlwings.
3. Make sure the Python file is in the same directory as the Excel workbook. If the code doesn't run correctly, navigate to a directory you would like to use, run the command below with your project's name, and copy the contents of this repository into their corresponding files.
```
xlwings quickstart ProjectName
```
4. Have fun :). Click the "Refresh" button to reload the metrics with new API requests.


