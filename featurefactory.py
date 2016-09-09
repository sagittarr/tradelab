from graphlab import SArray, SFrame
import abc

class Feature(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate(self, sf):
        pass

class crossMA(Feature):
    price = 'close'
    def __init__(self, MA1, MA2):
        self.MA1 = MA1
        self.MA2 = MA2
        self.name = str(MA1) + '/' + str(MA2)

    def generate(self, sf):
        sma1 = sf[self.price].rolling_mean(-1*self.MA1, 0)
        sma2 = sf[self.price].rolling_mean(-1*self.MA2, 0)
        diff = sma1 - sma2
        signals= [None]*len(sma1)
        for i in xrange(1, len(diff)):
            if diff[i] and diff[i-1]:
                if diff[i] > 0 and diff[i-1] < 0:
                    signals[i] = 1
                elif diff[i] < 0 and diff[i-1] > 0:
                    signals[i] = -1
                else:
                    signals[i] = 0
        sf.add_column(SArray(signals), name= self.name)
        return self.name

class RSI(Feature):
    _default_period = 14

    def __init__(self, period, column):
        self.column = column
        if not period:
            self.period = self._default_period
        else:
            self.period = period

    @classmethod
    def compute(cls, sf, period, column):
        gain,loss = 0, 0
        rsi = [None]*len(sf[column])
        j = 0
        for i in xrange(len(sf[column])):
            v = sf[column][i]
            if v > 0:
                gain += v
            else:
                loss += -1 * v
            if i >= period - 1:
                if loss == 0 and gain == 0:
                    rsi[i] = 50.
                elif loss == 0:
                    rsi[i] = 100.
                else:
                    rsi[i] = 100. - 100./(1. + gain/float(loss))
                u = sf[column][j]
                gain -= u if u > 0 else 0
                loss += u if u < 0 else 0
                j += 1
        return SArray(rsi)

    def generate(self, sf):
        if self.column in sf.column_names():
            name = 'rsi'+str(self.period)
            sf.add_column(RSI.compute(sf, self.period, self.column), name= name)
            return name
        else:
            raise Exception(str(self.column) + ' is not found in SFrame.')
            
            
class FeatureFactory(object):

    @staticmethod
    def generate_moving_average(sf, column = 'close', new_column='MA', period = 14):
        if column in sf.column_names():
            sf.add_column(sf[column].rolling_mean(-1*period, 0), name = new_column+str(period))
            return new_column+str(period)
        else:
            raise Exception(column + 'not in sframe')

    @staticmethod
    def generate_rsi(sf, column='gain', n=14):
        rsi = RSI(n, column)
        return rsi.generate(sf)

    @staticmethod
    def generate(sf, func, feat_name):
        sf[feat_name] = func()
# rsi = RSI(14, 'gain')
# print type(RSI)
# sf = SFrame({'a':[1,2,3]})
# FeatureFactory.generate(sf, lambda : sf['a'] + 1, 'b')
# print sf

