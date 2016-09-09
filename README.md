# tradelab
trading strategy research
  --machine learning based stock forecasting and trading strategy lab
  
data: stock daily price from yahoo finance
feature: generate multiple stock signals from previous daily data. e.g RSI, SMA, crossSMA
model: machine learning classifier(train with 80% data, tested with 20%). e.g Decision Tree, Random Froest, Logistic regression
strategy: make trade based on model's prediction
backtest: review the model's prediction with metrics, and evaluate the simulated portfolio performance

lib dependency: GraphLab Create, pandas, ffn, matplot.

