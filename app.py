from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
from binance.client import Client
import pandas as pd
from config import *

import strategy.basic_rsi as strategy


def get_historical_kline_df(symbol, interval, start_date, end_date):
    '''
    Get raw candlesticks data returned from client and decorate into dataframe format
    # Response is in below format
    # [
    #     1499040000000,        // Open time
    #     "0.01634790",         // Open
    #     "0.80000000",         // High
    #     "0.01575800",         // Low
    #     "0.01577100",         // Close
    #     "148796.11427815"     // Volume
    #     1499644799999,        // Close time
    #     "2434.19055334"       // Quote asset volume
    #     308,                  // Number of trades
    #     "1756.87402397"       // Taker buy base asset volume
    #     "28.46694368"         // Taker buy quote asset volume
    #     "17928899.62484339"   // Ignore
    # ]
    '''
    candlesticks = client.get_historical_klines(symbol, interval, start_date, end_date)
    hist_df = pd.DataFrame(candlesticks)
    hist_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVol', 'TradeNo', 'TakerBuyBaseAssetVol', 'TakerBuyQuoteAssetVol', 'Ignore']
    hist_df['Date'] = pd.to_datetime(hist_df['Date'], unit='ms')
    hist_df.set_index('Date', inplace=True)
    hist_df = hist_df[['Open', 'High', 'Low', 'Close', 'Volume']]
    hist_df = hist_df.apply(pd.to_numeric)

    return hist_df


if __name__ == '__main__':

    client = Client(API_KEY, API_SECRET)

    df = get_historical_kline_df("XRPUSDT", Client.KLINE_INTERVAL_5MINUTE, "04/01/2021", "05/03/2021")
    print('ok')

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(strategy.BasicRSITestStrategy)

    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=df)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(0.0025)
    cerebro.broker.set_coc(True)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.4f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.4f' % cerebro.broker.getvalue())