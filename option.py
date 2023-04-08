# -*- coding: utf-8 -*-
import pandas as pd


class OptionChain:
    """class to deal with optionchain data"""

    def __init__(self, df):
        self.data = df
        self.expiry_tags = df['expiration'].sort_values().unique().tolist()

    def get_atm(self, underlying_price, option_type, expiration, strike_num=0):
        """get data for at the money option
        strike_num: below or above n level for normal atm option"""
        data_ = self.data[(self.data['expiration'] == expiration) & (self.data['option_type'] == option_type)].copy()
        data_.sort_values(by='strike', inplace=True)
        atm_data = data_[lambda x: x['strike'].sub(underlying_price).abs().pipe(lambda y: y == y.min())]
        if strike_num != 0:
            atm_strike = atm_data['strike'].values[0]
            strikes = data_['strike'].unique().tolist()
            idx_atm = strikes.index(atm_strike)
            if option_type == 'C':
                atm_strike_ = strikes[idx_atm + strike_num]
            else:
                atm_strike_ = strikes[idx_atm - strike_num]
            atm_data = data_[data_['strike'] == atm_strike_]
        return atm_data

    def get_option(self, option_type, expiration, strike):
        """get data for certain option"""
        data_ = self.data[(self.data['expiration'] == expiration) &
                          (self.data['option_type'] == option_type) &
                          (self.data['strike'] == strike)].copy()
        return data_

    def get_sub(self):
        """subset option chains terms on maturity"""
        subs = ()
        for expiry in self.expiry_tags:
            tmp = self.data[self.data['expiration'] == expiry]
            tmp.sort_values(by='strike', inplace=True)
            subs += (tmp,)
        return subs


class OptionChainCSVParser:
    """parse option chain data from csv file
    cls attributes are column indexes for option or underlying data"""

    option_params = (2, 3, 4, 5, 6, 7, 8, 9, 10, 25,
                     11, 12, 13, 14, 17,
                     19, 20, 21, 22, 23, 24)
    underlying_params = (0, 15, 16, 18)
    underlying_symbol = 0
    snapshot_time = 1
    option_symbol = 2
    expiration = 3
    csv_file = 'UnderlyingOptionsIntervals_1800sec_calcs_oi_2021-04-26.csv'

    def parse(self):
        df = pd.read_csv(self.csv_file)
        columns = df.columns
        und_symbol_col = columns[self.underlying_symbol]
        option_symbol_col = columns[self.option_symbol]
        snapshot_time_col = columns[self.snapshot_time]

        unds = df[und_symbol_col].unique().tolist()
        unds_with_options = {und: df.loc[df[und_symbol_col] == und, option_symbol_col].unique().tolist() for und in unds}

        data_optionchain = {}
        data_und = {}
        und_cols = columns[list(self.underlying_params)].tolist() + [snapshot_time_col]
        option_cols = columns[list(self.option_params)].tolist()
        for und in unds:
            data_optionchain[und] = {}
            data_und[und] = {}
            options = unds_with_options[und]
            for option in options:
                df_und = df.loc[(df[und_symbol_col] == und) & (df[option_symbol_col] == option), und_cols].drop_duplicates()
                df_und.set_index(snapshot_time_col, drop=True, inplace=True)
                df_chain = pd.DataFrame({}, columns=['optionchain'], index=df_und.index)
                option_chains = []
                for time in df_und.index:
                    df_option_chain = df.loc[(df[und_symbol_col] == und) &
                                             (df[option_symbol_col] == option) &
                                             (df[snapshot_time_col] == time), option_cols]
                    option_chains.append(df_option_chain)
                df_chain['optionchain'] = option_chains
                data_und[und][option] = df_und
                data_optionchain[und][option] = df_chain
        return data_und, data_optionchain
