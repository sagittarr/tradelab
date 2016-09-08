import abc
import pandas as pd


class Strategy(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def simulate_trade(self, data, capital, cost):
        pass

class SimpleDayTrade(Strategy):
    def __init__(self, prediction):
        self.prediction = prediction

    def simulate_trade(self, data, capital, cost):
        if len(data) != len(self.prediction):
            raise Exception('size of data %d and prediction %d not match.', len(data), len(self.prediction))
        n = len(self.prediction)
        asset = []
        for i in xrange(n):
            if data[i]['datetime'] != self.prediction[i]['datetime']:
                raise Exception('datetime not match %s %s', data['datetime'][i], self.prediction['datetime'][i])
            asset.append(capital*(data[i]['close']/data[i]['open']) - 2.*cost if self.prediction[i]['prediction'] == 1 else capital)
            capital = asset[-1]
        return pd.Series(data=asset)

def backtest(data, strategy, capital, cost):
    asset = strategy.simulate_trade(data, capital, cost)
    df = pd.DataFrame(data = {'datetime': data['datetime'], 'benchmark': 100.*data['close']/data['close'][0], 'algo': 100.*asset/asset[0]})
    perf = df.set_index('datetime')

    df = pd.DataFrame(data = {'datetime': data['datetime'],'benchmark': data['close'], 'asset': asset})
    portf = df.set_index('datetime')
    return (perf, portf)

