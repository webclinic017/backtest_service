# -*- coding: utf-8 -*-
import backtrader as bt
from option import OptionChain


class IntradayStraddleStrategy(bt.Strategy):
    """Intraday trade on selling straddle"""

    """
    :param datetime: datetime index for bar data
    :param df_optionchain: option chain data fetched from outside data source
    :param callput_n: straddle combo for option chain of first n expiries
    """
    params = dict(datetimes=None,
                  df_optionchain=None,
                  callput_num=2)

    def __init__(self):
        # data records for option position by strike
        self.call_positions_by_k = [0] * self.p.callput_num
        self.put_positions_by_k = [0] * self.p.callput_num

        # underlying data
        self.und_data = self.datas[0]

        # empty datafeeds for traded options used for backtrader cerebro
        self.call_data = {data._name: data for data in self.datas if 'call' in data._name}
        self.put_data = {data._name: data for data in self.datas if 'put' in data._name}

    def next(self):
        """trading strategy core: sell straddle combos on first bar;
        update data bar on positioned options for backtrader cerebro"""

        und_price = self.und_data.close[0]
        idx = len(self.datas[0])

        # get option chain data for current bar
        datetimes = self.p.datetimes[idx - 1]
        option_chain = OptionChain(self.get_optionchain_data(datetimes))

        if idx == 1:  # first bar
            for i in range(self.p.callput_num):
                # choose option chains with certain maturity
                expiration = option_chain.expiry_tags[i]

                # get atm options for straddle combos
                atm_call_tmp = option_chain.get_atm(und_price, 'C', expiration)
                atm_put_tmp = option_chain.get_atm(und_price, 'P', expiration)

                # get option prices (middle quotes) for straddle combos
                call_close_tmp = (atm_call_tmp['bid'].values[0] + atm_call_tmp['ask'].values[0]) / 2
                put_close_tmp = (atm_put_tmp['bid'].values[0] + atm_put_tmp['ask'].values[0]) / 2

                # get strikes
                call_k_tmp = atm_call_tmp['strike'].values[0]
                put_k_tmp = atm_put_tmp['strike'].values[0]

                # get empty datafeeds prepared for traded options
                call_data_tmp = self.call_data[f'call{i}']
                put_data_tmp = self.put_data[f'put{i}']

                # set close prices on current bar of datafeeds prepared for traded options
                call_data_tmp.close[0] = call_close_tmp
                put_data_tmp.close[0] = put_close_tmp

                # sell straddel combo
                self.sell(data=call_data_tmp, size=1)
                self.sell(data=put_data_tmp, size=1)

                # records positioned options by strike
                self.call_positions_by_k[i] = call_k_tmp
                self.put_positions_by_k[i] = put_k_tmp

                print(self.p.datetimes[idx - 1], i, call_close_tmp, put_close_tmp)
        else:  # with position
            for i in range(self.p.callput_num):
                # choose option chains with certain maturity
                expiration = option_chain.expiry_tags[i]

                # get datafeeds prepared for traded options
                call_data_tmp = self.call_data[f'call{i}']
                put_data_tmp = self.put_data[f'put{i}']

                # get positioned options by strike
                position_call_tmp = option_chain.get_option('C', expiration, self.call_positions_by_k[i])
                position_put_tmp = option_chain.get_option('P', expiration, self.put_positions_by_k[i])

                # get option prices (middle quotes) for straddle combos
                call_close_tmp = (position_call_tmp['bid'].values[0] + position_call_tmp['ask'].values[0]) / 2
                put_close_tmp = (position_put_tmp['bid'].values[0] + position_put_tmp['ask'].values[0]) / 2

                # set close prices on current bar of datafeeds prepared for traded options
                call_data_tmp.close[0] = call_close_tmp
                put_data_tmp.close[0] = put_close_tmp

                print(self.p.datetimes[idx - 1], i, call_close_tmp, put_close_tmp)

    def log(self, txt, dt=None):
        """ Logging function for strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        """override order monitoring method"""

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行, %.2f, %s' % (order.executed.price, order.data._name))
            elif order.issell():
                self.log('卖单执行, %.2f, %s' % (order.executed.price, order.data._name))

    def get_optionchain_data(self, _datetime):
        """get option data based on given datetime """
        data = self.p.df_optionchain.loc[_datetime, 'optionchain']
        return data
