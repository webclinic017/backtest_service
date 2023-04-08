# -*- coding: utf-8 -*-

und = '^VIX'  # underlying ticker
option = 'VIX'  # option ticker
front_num = 3  # number of traded combos based on ascending maturities

if __name__ == '__main__':
    from data import *
    from option import *
    from strategy import *

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # fetch underlying and optionchain data indexed by datetimes
    und_data, optionchain_data = OptionChainCSVParser().parse()

    cerebro = bt.Cerebro()

    # underlying data
    und_data_tmp = und_data[und]
    df = und_data_tmp[option]

    # optionchain data
    optionchain_data_tmp = optionchain_data[und]
    df_optionchain = optionchain_data_tmp[option]

    # feeds underlying data
    option_tag = und + '_' + option
    cerebro.adddata(feed_data(df), name=option_tag)

    datetimes = df.index

    # feeds emtpy data for positioned straddel combos
    call = pd.DataFrame({}, index=datetimes, columns=df.columns)
    put = pd.DataFrame({}, index=datetimes, columns=df.columns)
    for n in range(front_num):
        cerebro.adddata(feed_data(call), name=f'call{n}')
        cerebro.adddata(feed_data(put), name=f'put{n}')

    cerebro.addstrategy(IntradayStraddleStrategy, datetimes=datetimes, df_optionchain=df_optionchain, callput_num=front_num)
    cerebro.broker.set_coc(True)  # intraday order dealed upon setting!!!
    cerebro.broker.setcash(1000)
    cerebro.run()
    cerebro.plot(volume=False, iplot=False)
