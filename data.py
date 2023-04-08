# -*- coding: utf-8 -*-
import backtrader as bt
import pandas as pd


class OptionChainData(bt.feeds.PandasData):
    """datafeeds for extra column on optionchain data"""
    params = (('optionchain', -1),)
    lines = ('optionchain',)


def feed_data(df, plot=False):
    """transfer dataframe to baktrader pandas datafeed;
    str datetime index of raw dataframe should be transformed with datetime format"""
    df_ = df.copy()
    df_.index = pd.to_datetime(df_.index)
    data = bt.feeds.PandasData(dataname=df_, datetime=None, open=1, high=2, low=1, close=3, volume=-1, openinterest=-1, plot=plot)
    return data
