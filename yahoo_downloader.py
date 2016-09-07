from datetime import datetime
from yahoo_finance import Share
from graphlab import SFrame

class yh_downloader(object):
    def __init__(self):
        pass
    @staticmethod
    def download(symbol, start_date, end_date):
        stock = Share(symbol)
        # ^GSPC is the Yahoo finance symbol to refer S&P 500 index
        # we gather historical quotes from 2001-01-01 up to today
        hist_quotes = stock.get_historical(start_date, end_date)
        l_date = []
        l_open = []
        l_high = []
        l_low = []
        l_close = []
        l_volume = []
        # reverse the list
        hist_quotes.reverse()
        for quotes in hist_quotes:
            l_date.append(quotes['Date'])
            l_open.append(float(quotes['Open']))
            l_high.append(float(quotes['High']))
            l_low.append(float(quotes['Low']))
            l_close.append(float(quotes['Adj_Close']))
            l_volume.append(int(quotes['Volume']))

        sf = SFrame({'datetime' : l_date,
            'open' : l_open,
            'high' : l_high,
            'low' : l_low,
            'close' : l_close,
            'volume' : l_volume})
        # datetime is a string, so convert into datetime object
        sf['datetime'] = sf['datetime'].apply(lambda x:datetime.strptime(x, '%Y-%m-%d'))
        return sf