from graphlab import SArray

class feature_generator(object):

    @staticmethod
    def generate_moving_average(sf, column = 'close', new_column='MA', period = 14):
        if column in sf.column_names():
            sf.add_column(sf[column].rolling_mean(-1*period, 0), name = new_column)
        return sf

    @staticmethod
    def generate_rsi(sf, column='gain', n=14):
        gain,loss = 0, 0
        rsi = [None]*len(sf[column])
        j = 0
        for i in xrange(len(sf[column])):
            v = sf[column][i]
            if v > 0:
                gain += v
            else:
                loss += -1 * v
            if i >= n - 1:
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
        sf.add_column(SArray(rsi), name='rsi')

