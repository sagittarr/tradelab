import graphlab as gl
import time
from featurefactory import *
import matplotlib.pyplot as plt
from BackTesting import *
import pandas as pd
import ffn


# product_key = '753F-AEC9-A3FB-6D7B-B973-6AF1-7153-C35C'
# gl.product_key.set_product_key(product_key)


data = gl.SFrame('SP500_daily.bin/')
# add the outcome variable, 1 if the trading session was positive (close>open), 0 otherwise
data['outcome'] = data.apply(lambda x: 1 if x['close'] > x['open'] else -1)
# they will be useful to backtest the model, later
data['ho'] = data['high'] - data['open'] # distance between Highest and Opening price
data['lo'] = data['low'] - data['open'] # distance between Lowest and Opening price
data['gain'] = data['close'] - data['open']
rsi_14 = FeatureFactory.generate_rsi(data, n = 14)
rsi_5 = FeatureFactory.generate_rsi(data, n = 5)
ma_20 = FeatureFactory.generate_moving_average(data, period=20)
ma_5 = FeatureFactory.generate_moving_average(data, period=5)
crossMA1_10 = crossMA(1, 10).generate(data)
crossMA5_20 = crossMA(5, 20).generate(data)

ts = gl.TimeSeries(data, index='datetime')
# add the outcome variable, 1 if the bar was positive (close>open), 0 otherwise
ts['outcome'] = ts.apply(lambda x: 1 if x['close'] > x['open'] else -1)
# ts['ma5-20'] = ts[ma_5] - ts[ma_20]
# GENERATE SOME LAGGED TIMESERIES
ts_1 = ts.shift(1) # by 1 day
ts['dRtn'] = ts['close']/ts_1['close']
ts['idRtn'] = ts['close']/ts['open']
ts_1 = ts.shift(1) # by 1 day
ts_2 = ts.shift(2)
ts_3 = ts.shift(3)
ts['open_above_close'] = ts['open'] > ts_1['close']
ts['dRtn'] = ts['close']/ts_1['close']
ts['idRtn'] = ts['close']/ts['open']
ts['jump'] = ts['open'] > ts_1['high']
ts['aboveMA'] = ts['open'] > ts_1[ma_20]
ts['rsi14'] = ts_1['rsi14']
ts['rsi5'] = ts_1['rsi5']
ts[crossMA5_20] = ts_1[crossMA5_20]
ts[crossMA1_10] = ts_1[crossMA1_10]
# ts[ma_20] = ts_1[ma_20]
# ts[ma_5] = ts_1[ma_5]
# ts['ma5-20'] = ts_1['ma5-20']
# ts['rsi_cmp'] = ts_1['rsi'] > ts_2['rsi']
# ts['rsi_cmp1'] = ts_2['rsi'] > ts_3['rsi']
ts['3dRtn'] = ts_1['dRtn']*ts_2['dRtn']*ts_3['dRtn']
# ts['feat5'] = ts_1['rsi'] <30
# ts['feat6'] = ts_1['rsi'] >70

features = ['open_above_close','jump','aboveMA', rsi_14, rsi_5, '3dRtn', crossMA5_20, crossMA1_10]
# 'feat2','feat3','feat4'

ratio = 0.8 # 80% of training set and 20% of testing set
training = ts.to_sframe()[0:round(len(ts)*ratio)]
training = training.dropna()
testing = ts.to_sframe()[round(len(ts)*ratio):]
model = gl.decision_tree_classifier.create(training, validation_set=None,
                                                   target='outcome', features=features,
                                                   max_depth=3, verbose=False)

# model = gl.random_forest_classifier.create(training, target='outcome', features=features,
#                                       validation_set=None, verbose=False, num_trees = 8)

# model = gl.logistic_classifier.create(training, target='outcome', features=features, validation_set=None, verbose=False)

# model = gl.boosted_trees_classifier.create(training, target='outcome', features=features,
#                                            validation_set=None, max_iterations=40, verbose=False)

predictions = model.predict(testing)
# and we add the predictions  column in testing set
testing['predictions'] = predictions

# let's see the first 10 predictions, compared to real values (outcome column)
# print testing[['datetime', 'outcome', 'predictions']].head(10)
print 'training accuracy: ' + str(model.evaluate(training)['accuracy'])
print 'testing accuracy: ' +  str(model.evaluate(testing)['accuracy'])
print 'begin: ' + str(testing['close'][0]),'end: ' + str(testing['close'][-1])


predictions = gl.SFrame({'datetime': testing['datetime'], 'prediction': predictions})
strategy = SimpleDayTrade(predictions)
perf, portf = backtest(testing, strategy, 30000, 7)

print ffn.core.calc_stats(portf).display()
print 'portfolio value: %d', portf['asset'][-1]
gl.canvas.set_target('browser')
model.show()
plt.plot(perf,marker='o')
plt.show()



