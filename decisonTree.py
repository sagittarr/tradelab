import graphlab as gl

product_key = '753F-AEC9-A3FB-6D7B-B973-6AF1-7153-C35C'
gl.product_key.set_product_key(product_key)

gl.canvas.set_target('browser')
qq = gl.SFrame('SP500_daily.bin/')
# add the outcome variable, 1 if the trading session was positive (close>open), 0 otherwise
qq['outcome'] = qq.apply(lambda x: 1 if x['close'] > x['open'] else -1)
# they will be useful to backtest the model, later
qq['ho'] = qq['high'] - qq['open'] # distance between Highest and Opening price
qq['lo'] = qq['low'] - qq['open'] # distance between Lowest and Opening price
qq['gain'] = qq['close'] - qq['open']

ts = gl.TimeSeries(qq, index='datetime')
# add the outcome variable, 1 if the bar was positive (close>open), 0 otherwise
ts['outcome'] = ts.apply(lambda x: 1 if x['close'] > x['open'] else -1)


# GENERATE SOME LAGGED TIMESERIES
ts_1 = ts.shift(1) # by 1 day
ts_2 = ts.shift(2)

ts['feat1'] = ts['open']     > ts_1['close']
ts['feat2'] = ts_1['close']  > ts_2['close']
ts['feat3'] = ts_1['open']   > ts_2['close']
ts['feat4'] = ts_2['close']  > ts_2['open']
ts['feat5'] = ts_1['lo']
ts['feat6'] = ts_1['ho']

# ts['feat5'] = ts_1['volume'] > ts_2['volume']

features = ['feat1','feat2','feat3','feat4','feat5','feat6']


ratio = 0.8 # 80% of training set and 20% of testing set
training = ts.to_sframe()[0:round(len(ts)*ratio)]
testing = ts.to_sframe()[round(len(ts)*ratio):]
decision_tree = gl.decision_tree_classifier.create(training, validation_set=None,
                                                   target='outcome', features=features,
                                                   max_depth=6, verbose=False)

predictions = decision_tree.predict(testing)
# and we add the predictions  column in testing set
testing['predictions'] = predictions

# let's see the first 10 predictions, compared to real values (outcome column)
# print testing[['datetime', 'outcome', 'predictions']].head(10)
print decision_tree.evaluate(training)['accuracy']
print decision_tree.evaluate(testing)['accuracy']
predictions_prob = decision_tree.predict(testing, output_type="probability")
print predictions_prob
buy = [testing['predictions'] == 1]
print buy
pnl = testing[testing['predictions'] == 1]['datetime','gain']
print sum(pnl['gain'])
z = [pnl['gain'][0]]
for x in xrange(1,len(pnl)):
    z.append(z[x-1] + pnl['gain'][x])
pnl.add_column(gl.SArray(z),name = 'return')
# decision_tree.show(view='Tree')
pnl.show()
# while True:
#     pass


