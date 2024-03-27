# -*- coding: utf-8 -*-
"""Aisha's_Stock_Price_Predictive_Analysis_.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1c84gLSIhhr7iKWAYKaKRpne1RYiBhJGH

# **S&P500 Stock Price Analysis**
by Juma Aisha
"""

!pip install pmdarima

# Commented out IPython magic to ensure Python compatibility.
# importing libraries

import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

#All necessary plotly libraries
import plotly as plotly
import plotly.io as plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

# stats tools
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Arima Model
from pmdarima.arima import auto_arima

# metrics
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math

# LSTM
from tensorflow import keras
from tensorflow.keras.layers import Dense,LSTM,Dropout,Flatten
from tensorflow.keras import Sequential

import warnings
warnings.filterwarnings("ignore")
# %matplotlib inline

"""# Reading the dataset"""

# Reading the dataset
df = pd.read_csv("sp500_data.csv")
df.head(3)

df.tail(5)

df.info()

# Convert date feature from Object datatype to datetime format
df['Date'] = pd.to_datetime(df['Date'])

df = df.set_index(df['Date']).sort_index() # setting date feature as our index
print(df.shape)
df.sample(5)

df.describe().T

# Checking the data types of  columns
# checking the count of null values -> 0
df.info()

df.columns

data = df[['Date', 'Open', 'High', 'Low', 'Close', 'Adjusted Close', 'Volume']]
data

"""# **Data Visualizing & Preprocessing**"""

data['Volume'].plot(figsize=(15,5))

data['Close'].plot(figsize=(15,5))

sns.kdeplot(data['Close'], shade=True)



"""#### checking the distribution and skewdness"""

for feature in data.select_dtypes("number").columns:

    plt.figure(figsize=(16,5))
    sns.distplot(data[feature], hist_kws={"rwidth": 0.9})
    plt.xlim(data[feature].min(), data[feature].max())
    plt.title(f"Distribution shape of {feature.capitalize()}\n", fontsize=15)
    plt.tight_layout()
    plt.show()



"""##### Visualizing the distribution of the dependent varibale using a Frequency Distribution plot and a Box plot"""

plt.figure(figsize=(16,5))
data["Close"].plot(kind="hist", bins=100, rwidth=0.9)
plt.title("Close Price): value distribution")
plt.xlabel("Closed ")
plt.tight_layout()
plt.show()

plt.figure(figsize=(16,5))
data["Close"].plot(kind="box", vert=False)
plt.title("Close Price: Frequency distribution\n", fontsize=15)
plt.xlabel("\nClosed(g/km)")
plt.yticks([0], [''])
plt.ylabel("Closed\n", rotation=90)
plt.tight_layout()
plt.show()

# Adding Return Column

data['Return'] = (data['Adjusted Close']-data['Open'])/data['Open']

# making a copy for later use
stocks_data = data.copy()

data.sample(5)

# visualising the closing price of the dataset using plotly

fig = px.line(data,x="Date",y="Close",title="Closing Price")
fig.update_xaxes(rangeslider_visible=True,rangeselector=dict(
    buttons=list([
        dict(count=1,label="1m",step="month",stepmode="backward"),
        dict(count=6,label="6m",step="month",stepmode="backward"),
        dict(count=1,label="YTD",step="year",stepmode="todate"),
        dict(count=1,label="1y",step="year",stepmode="backward"),
        dict(step="all")
])))

# Visualizing Returns

fig = px.line(data,x="Date",y="Return",title="Returns : Range Slider and Selectors")
fig.update_xaxes(rangeslider_visible=True,rangeselector=dict(
    buttons=list([
        dict(count=1,label="1m",step="month",stepmode="backward"),
        dict(count=6,label="6m",step="month",stepmode="backward"),
        dict(count=1,label="YTD",step="year",stepmode="todate"),
        dict(count=1,label="1y",step="year",stepmode="backward"),
        dict(step="all")
])))

# Visualizing Open, High, Close and Low of a stock on a given time frame using candlestick
fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                                    open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'])])
fig.show()

# OHLC plots of Open, High, Low and Close with Volume
fig = make_subplots(rows=2, cols=1)

#OHLC Plot
fig.add_trace(go.Ohlc(x=data.Date, open=data.Open, high=data.High, low=data.Low, close=data.Close, name='Price'),row=1, col=1)
#Volume PLot
fig.add_trace(go.Scatter(x=data.Date, y=data.Volume, name='Volume'), row=2, col=1)

fig.update(layout_xaxis_rangeslider_visible=False)
fig.show()

"""## Shifting and lags

We can shift index by desired number of periods with an optional time frequency. This is useful when comparing the time series with a past of itself
"""

fig = go.Figure()
data['Close_M'] = data["Close"].asfreq('d')
data['Lag_Close_M'] = data['Close'].asfreq('d').shift(10)
fig.add_trace(go.Scatter(x=data.Date,y=data.Close_M,name='Close_M'))
fig.add_trace(go.Scatter(x=data.Date,y=data.Lag_Close_M,name='Lag_Close_M'))
fig.show()

fig = go.Figure()
data['Volume_M'] = data["Volume"].asfreq('d')
data['Lag_Volume_M'] = data['Volume'].asfreq('d').shift(10)
fig.add_trace(go.Scatter(x=data.Date,y=data.Volume_M,name='Volume_M'))
fig.add_trace(go.Scatter(x=data.Date,y=data.Lag_Volume_M,name='Lag_Volume_M'))
fig.show()

"""# Time Series Data Analysis - Resampling

"""

# downsampling from months to years to decrease data points, where A represents "year end frequency"
data.resample(rule='A').max().tail(5)

# Here we got the max feature values of each year for the last 5 years

# visualize the max Close values of all years

data['Close'].resample(rule='A').max().plot(figsize=(15,5))

"""# Technical Indicators to visualize a stock pattern.

## Simple Moving Average
"""

data.head()

#SMA
# the average of prices over a given interval of time to determine the trend of the stock with slow SMA (SMA_15) and fast SMA (SMA_5)
data['SMA_5'] = data['Close'].rolling(5).mean().shift()
data['SMA_15'] = data['Close'].rolling(15).mean().shift()


fig = go.Figure()
fig.add_trace(go.Scatter(x=data.Date,y=data.SMA_5,name='SMA_5'))
fig.add_trace(go.Scatter(x=data.Date,y=data.SMA_15,name='SMA_15'))
fig.add_trace(go.Scatter(x=data.Date,y=data.Close,name='Close', opacity=0.3))
fig.show()

"""## Exponential Moving Average (EMA)

"""

#EMA

data['EMA_5'] = data['Close'].ewm(5).mean().shift()
data['EMA_15'] = data['Close'].ewm(15).mean().shift()

fig = go.Figure()
fig.add_trace(go.Scatter(x=data.Date,y=data.EMA_5,name='EMA_5'))
fig.add_trace(go.Scatter(x=data.Date,y=data.EMA_15,name='EMA_15'))
fig.add_trace(go.Scatter(x=data.Date,y=data.Close,name='Close', opacity=0.3))
fig.show()

# Now lets compare SMA's and EMA's

fig = go.Figure()
fig.add_trace(go.Scatter(x=data.Date,y=data.SMA_5,name='SMA_5'))
fig.add_trace(go.Scatter(x=data.Date,y=data.EMA_5,name='EMA_5'))
fig.add_trace(go.Scatter(x=data.Date,y=data.Close,name='Close', opacity=0.3))
fig.show()
# EMA_5 is performing better than SMA_5 as it is closer to CLosing price of Stock.

"""# Time Series Decomposition

"""

series = data.Close
result = seasonal_decompose(series, model='additive',period=1) # The frequncy is daily
figure = result.plot()

series = data.Close
result = seasonal_decompose(series, model='additive',period=365) # The frequncy is yearly
figure = result.plot()

series = data.Close
result = seasonal_decompose(series, model='additive',period=366) # The frequncy is yearly
figure = result.plot()

"""# Stationary Test / ADF Test"""

#Test for staionarity
def test_stationarity(timeseries):

    #Determing rolling statistics
    rolmean = timeseries.rolling(12).mean()
    rolstd = timeseries.rolling(12).std()

    #Plot rolling statistics:
    plt.figure(figsize=(15,5))
    plt.plot(timeseries,color='blue',label='Original')
    plt.plot(rolmean,color='red',label='Rolling Mean')
    plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean and Standard Deviation')
    plt.show(block=False)

    print("Results of dickey fuller test")
    adft = adfuller(timeseries,autolag='AIC')
    # output for dft will give us without defining what the values are.
    #hence we manually write what values does it explains using a for loop
    output = pd.Series(adft[0:4],index=['Test Statistics','p-value','No. of lags used','Number of observations used'])
    print(output)

test_stationarity(data['Close'])

"""

Through the above graph, we can see the increasing mean and standard deviation and hence **our series is not stationary.**

We see that the p-value is greater than 0.05 so we cannot reject the Null hypothesis. Also, the test statistics is greater than the critical values. so the data is non-stationary.

### DIFFERENCING:

"""

data['First Difference']=data['Close']-data['Close'].shift(1)

adft = adfuller(data['First Difference'].dropna(),autolag='AIC')
output = pd.Series(adft[0:4],index=['Test Statistics','p-value','No. of lags used','Number of observations used'])
print(output)

data['First Difference'].plot()

"""Our data is now Stationary

# Autocorrelation and Partial Autocorrelation
"""

plot_acf(data["First Difference"].dropna(),lags=5,title="AutoCorrelation")
plt.show()

# As all lags are either close to 1 or at least greater than the confidence interval, they are statistically significant.
# the diverging blue region is confidence interval

plot_pacf(data["First Difference"].dropna(),lags=5,title="Partial AutoCorrelation")
plt.show()

"""Here these two graphs will help us to find the p and q values.

    Partial AutoCorrelation Graph is for the p-value.
    AutoCorrelation Graph for the q-value.

# Model Forecasting

## Rolling ARIMA

### Split the data
"""

stocks_data = stocks_data.resample('D').ffill()
stocks_data.dropna(inplace=True)
df_train, df_valid = stocks_data[:int(0.8*len(df))], stocks_data[int(0.8*len(df)):]
train = df_train['Close'].values
test = df_valid['Close'].values

"""**AUTO ARIMA**"""

model_autoARIMA = auto_arima(train, start_p=0, start_q=0,
                      test='adf',       # use adftest to find optimal 'd'
                      max_p=3, max_q=3, # maximum p and q
                      m=1,              # frequency of series
                      d=None,           # let model determine 'd'
                      seasonal=False,   # No Seasonality
                      start_P=0,
                      D=0,
                      trace=True,
                      error_action='ignore',
                      suppress_warnings=True,
                      stepwise=True)
print(model_autoARIMA.summary())
model_autoARIMA.plot_diagnostics(figsize=(15,8))
plt.show()

# fit the model
model_autoARIMA.fit(train)

# make predictions
predictions = model_autoARIMA.predict(n_periods=len(test))
predictions = pd.DataFrame(predictions, index=df_valid.index, columns=['Predicted'])
predictions

# plot the predictions
plt.plot(df_train.index, train, label='Training Data')
plt.plot(df_valid.index, test, label='Test Data')
plt.plot(predictions.index, predictions['Predicted'], label='Predicted')
plt.title('S&P 500 Stock Price Prediction')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.legend()
plt.show()

# evaluate the model
mse = mean_squared_error(test, predictions)
rmse = np.sqrt(mse)
print('Mean Squared Error:', mse)
print('Root Mean Squared Error:', rmse)



"""**ARIMA**"""

history = [x for x in train]
predictions = list()

# walk-forward validation
for t in range(len(df_valid)):
    model = ARIMA(history, order=(1,1,1))
    model_fit = model.fit()
    output = model_fit.forecast()
    yhat = output[0]
    predictions.append(yhat)
    obs = test[t]
    history.append(obs)

"""**Mean square error**


"""

# evaluate forecasts
rolling_mse = mean_squared_error(test, predictions)
print('Test MSE: %.3f' % rolling_mse)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_valid.Date,y=df_valid.Close,name='Close'))
fig.add_trace(go.Scatter(x=df_valid.Date,y=predictions,name='Forecast_Rolling_ARIMA'))
fig.show()

"""## ARIMA

**Functions to remove Trend and Seasonality**
"""

# method to be used later
def difference(dataset, interval=1):
    diff = list()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i-interval]
        diff.append(value)
    return np.array(diff)

def inverse_difference(history, yhat, interval=1):
    return yhat + history[-interval]

"""### Trend Differencing by using Daily Lag"""

differenced = difference(train)
model=ARIMA(differenced,order=(1,1,1))
model_fit=model.fit()
start=len(train)
end=len(train)+len(test)-1
forecast = model_fit.predict(start=start,end=end)

history = [x for x in train]
predicted_results = list()

# store predicted results
for yhat in forecast:
    inverted = inverse_difference(history, yhat)
    history.append(inverted)
    predicted_results.append(inverted)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_valid.Date,y=df_valid.Close,name='Close'))
fig.add_trace(go.Scatter(x=df_valid.Date,y=predicted_results,name='Forecast_ARIMA'))
fig.show()

mse_daily = mean_squared_error(df_valid['Close'],predicted_results)
print('Test MSE: %.3f' %mse_daily)

"""### Seasonal differencing using Seasonal lag"""

days_in_year=365
differenced = difference(train,days_in_year)
model=ARIMA(differenced,order=(1,1,1))
model_fit=model.fit()
start=len(train)
end=len(train)+len(test)-1
forecast = model_fit.predict(start=start,end=end)

history = [x for x in train]
predicted_results = list()

# store predicted results
for yhat in forecast:
    inverted = inverse_difference(history, yhat, days_in_year)
    history.append(inverted)
    predicted_results.append(inverted)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_valid.Date,y=df_valid.Close,name='Close'))
fig.add_trace(go.Scatter(x=df_valid.Date,y=predicted_results,name='Forecast_ARIMA'))
fig.show()

# evaluate forecasts
mse_seasonal = mean_squared_error(test, predicted_results)
print('Test MSE: %.3f' % mse_seasonal)

"""### Seasonal+Daily Differencing"""

days_in_year=365
differenced_S = difference(train,days_in_year)
differenced = difference(differenced_S)
model=ARIMA(differenced,order=(1,1,1))
model_fit=model.fit()
start=len(train)
end=len(train)+len(test)-1
forecast = model_fit.predict(start=start,end=end)

history = [x for x in train]
predicted_results = list()

# store predicted results
interval=366
for yhat in forecast:
    inverted = inverse_difference(history, yhat, interval)
    history.append(inverted)
    predicted_results.append(inverted)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_valid.Date,y=df_valid.Close,name='Close'))
fig.add_trace(go.Scatter(x=df_valid.Date,y=predicted_results,name='Forecast_ARIMA'))
fig.show()

# evaluate forecasts
mse_sd = mean_squared_error(test, predicted_results)
print('Test MSE: %.3f' % mse_sd)

# Therefore from above we can Conclude that lowest mse score was achieved by Seasonal differencing.
best_arima_mse = mse_seasonal

"""# LSTM


"""

training_values = np.reshape(train,(len(train),1))
scaler = MinMaxScaler()
training_values = scaler.fit_transform(training_values)
# assign training values
x_train = training_values[0:len(training_values)-1]
y_train = training_values[1:len(training_values)]
x_train = np.reshape(x_train,(len(x_train),1,1))

# creates model
model = Sequential()
model.add(LSTM(128,return_sequences=True,input_shape=(None,1)))
model.add(LSTM(64,return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

#compile the model
model.compile(optimizer='adam',loss='mean_squared_error')

# Train the model
model.fit(x_train,y_train,epochs=25,batch_size=8)

# lstm_prediction = model.predict(test)
# lstm_metrics =evaluate_model(y_test, lstm_prediction, "KNN")
# combined_metrics.append(lstm_metrics)
# lstm_metrics

# assign test and predicted values + reshaping + converting back from scaler
test_values = np.reshape(test, (len(test), 1))
test_values = scaler.transform(test_values)
test_values = np.reshape(test_values, (len(test_values), 1, 1))
predicted_price = model.predict(test_values)
predicted_price = scaler.inverse_transform(predicted_price)
predicted_price=np.squeeze(predicted_price)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_valid.index,y=df_valid.Close,name='Close'))
fig.add_trace(go.Scatter(x=df_valid.index,y=predicted_price,name='Forecast_LSTM'))
fig.show()

# evaluate forecasts
mse_lstm = mean_squared_error(test, predicted_price)
print('Test MSE: %.3f' % mse_lstm)

"""# Comparing model scores"""

models = ['Rolling ARIMA','ARIMA','LSTM']
lst_acc = [rolling_mse,best_arima_mse,mse_lstm]
MSE = pd.DataFrame({'Model': models, 'Mean Squared Error': lst_acc})
MSE.sort_values(by="Mean Squared Error")

data.head()

data.fillna(0, inplace=True)

data.isna().sum()

data

"""**CORRELATION**"""

corr = data.corr()
#Plot figsize
fig, ax = plt.subplots(figsize=(20,15))
#Generate Heat Map, allow annotations and place floats in map
sns.heatmap(corr, annot=True, cmap= 'coolwarm', square=True)
#show plot
plt.show()

data.columns



data.columns

new_data = data.drop(['Close_M', 'Lag_Close_M', 'Volume_M', 'Lag_Volume_M', 'SMA_5',
       'SMA_15', 'EMA_5', 'EMA_15', 'First Difference'],axis=1)
new_data



"""# **Modelling**"""

#Define features and target columns
X = new_data[[ 'Open', 'High', 'Low', 'Adjusted Close', 'Volume',
        'Return']]
y = new_data['Close']

X

y

corr = new_data.corr()
#Plot figsize
fig, ax = plt.subplots(figsize=(20,15))
#Generate Heat Map, allow annotations and place floats in map
sns.heatmap(corr, annot=True, cmap= 'coolwarm', square=True)
#show plot
plt.show()

from sklearn.preprocessing import MinMaxScaler
MinMax = MinMaxScaler()
X_scaled = MinMax.fit_transform(X)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train_scaled, X_test_scaled, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

X

X_scaled

from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor, ExtraTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor

from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

def MBE(ground_truth, prediction):
    return np.sum(ground_truth - prediction) / len(ground_truth)

def MABE(ground_truth, prediction):
    return np.sum(abs(ground_truth - prediction)) / len(ground_truth)

def rRMSE(ground_truth, prediction):
    return np.sqrt(mean_squared_error(ground_truth, prediction))/np.mean(ground_truth) * 100

def evaluate_model(ground_truth, prediction, model):
    metrics = {
        "R_Squared": r2_score(ground_truth, prediction),
        "RMSE": np.sqrt(mean_squared_error(ground_truth, prediction)),
        "MAPE": mean_absolute_percentage_error(ground_truth, prediction),
        "MBE": MBE(ground_truth, prediction),
        "rRMSE":  rRMSE(ground_truth, prediction),
        "MABE": MABE(ground_truth, prediction)
    }
    return pd.DataFrame(pd.Series(metrics), columns=[model])

combined_metrics = []





"""### Artifitial Neural Network (ANN)"""

input_layer = X.shape[1]
hidden_layer = 100

ANN = MLPRegressor(activation="relu",
                   hidden_layer_sizes = (hidden_layer, ),
                   learning_rate_init= 0.001,
                   momentum= 0.9,
                   max_iter= 300  #number of Epochs
                  )

ANN.fit(X_train_scaled, y_train)

ann_prediction = ANN.predict(X_test_scaled)

ann_metrics = evaluate_model(y_test,  ann_prediction, "ANN")
combined_metrics.append(ann_metrics)
ann_metrics

"""### **Support Vector Machine**"""

svm = SVR( kernel='rbf',
            degree=3,
            C=1.0,
            epsilon=0.1,)
svm.fit(X_train_scaled, y_train)

svm_prediction = svm.predict(X_test_scaled)

svm_metrics = evaluate_model(y_test,  svm_prediction, "SVM")
combined_metrics.append(svm_metrics)
svm_metrics

# defining parameter range
param_grid = {'C': [0.1, 1, 10, 100, 1000],
              'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
              'kernel': ['rbf']}

grid = RandomizedSearchCV(SVR(),param_grid, cv=3,scoring="neg_mean_squared_error",refit = True, verbose = 3, n_iter = 5)

# fitting the model for grid search
grid.fit(X_train_scaled, y_train)

# print best parameter after tuning
print(grid.best_params_)
# print how our model looks after hyper-parameter tuning
print(grid.best_estimator_)

svm_tuned_prediction = grid.predict(X_test_scaled)
svm_tuned_metrics = evaluate_model(y_test,  svm_tuned_prediction, "SVM_tuned")
combined_metrics.append(svm_tuned_metrics)
svm_tuned_metrics

"""### **Deep Neural Network (DNN)**"""

DNN = MLPRegressor(activation="relu",
                   hidden_layer_sizes = (100, 100),
                   learning_rate_init= 0.001,
                   momentum= 0.9,
                   max_iter= 300  #number of Epochs
                  )

DNN.fit(X_train_scaled, y_train)

dnn_prediction = DNN.predict(X_test_scaled)

dnn_metrics = evaluate_model(y_test,  dnn_prediction, "DNN")
combined_metrics.append(dnn_metrics)
dnn_metrics

"""### **Decision Tree Regressor**"""

decision_tree = DecisionTreeRegressor()
decision_tree.fit(X_train, y_train)
DT_prediction = decision_tree.predict(X_test)
dt_metrics = evaluate_model(y_test, DT_prediction, "Decision Tree")
combined_metrics.append(dt_metrics)
dt_metrics

param_grid = {'max_depth':[2,3,4,5,6,7,8],}

grid = RandomizedSearchCV(DecisionTreeRegressor(),param_grid, cv=3,scoring="neg_mean_squared_error",refit = True, verbose = 3, n_iter = 5)

# fitting the model for grid search
grid.fit(X_train, y_train)

print(grid.best_params_)
print(grid.best_estimator_)

DT_tuned_prediction = grid.predict(X_test)
DT_tuned_metrics = evaluate_model(y_test,  DT_tuned_prediction, "DecisionTree_tuned")
combined_metrics.append(DT_tuned_metrics)
DT_tuned_metrics

feature_importance_df = pd.DataFrame(decision_tree.feature_importances_, columns=['importance'])
feature_importance_df['feature'] = X_train.columns

plt.figure(figsize=(15, 6));
sns.barplot(x="importance", y="feature", data=feature_importance_df.sort_values(by = ['importance'], ascending = False).head(50))
plt.title('Decision Tree features importance');

"""### **Random Forest Regressor**"""

random_forest = RandomForestRegressor()
random_forest.fit(X_train, y_train)
RF_prediction = random_forest.predict(X_test)
rf_metrics =evaluate_model(y_test, RF_prediction, "Random Forest")
combined_metrics.append(rf_metrics)
rf_metrics

param_grid = {
              "n_estimators": [50,100,200,300],
              'max_depth':[2,3,4,5,6,7,8],
              }
grid = RandomizedSearchCV(RandomForestRegressor(),param_grid, cv=3,scoring="neg_mean_squared_error",refit = True, verbose = 3, n_iter = 5)

# fitting the model for grid search
grid.fit(X_train, y_train)

print(grid.best_params_)
print(grid.best_estimator_)

RF_tuned_prediction = grid.predict(X_test)
RF_tuned_metrics = evaluate_model(y_test,  RF_tuned_prediction, "RandomForest_tuned")
combined_metrics.append(RF_tuned_metrics)
RF_tuned_metrics

feature_importance_df = pd.DataFrame(random_forest.feature_importances_, columns=['importance'])
feature_importance_df['feature'] = X_train.columns

plt.figure(figsize=(15, 6));
sns.barplot(x="importance", y="feature", data=feature_importance_df.sort_values(by = ['importance'], ascending = False).head(50))
plt.title('Random Forest features importance');

"""**Linear Regression**"""

linear_regression = LinearRegression()
linear_regression.fit(X_train, y_train)
LR_prediction = linear_regression.predict(X_test)
lr_metrics =evaluate_model(y_test, LR_prediction, "Linear Regression")
combined_metrics.append(lr_metrics)
lr_metrics

lr = LinearRegression().fit(X_train, y_train)
print(f'Value of Coefficients - {lr.coef_}')

print(lr.intercept_)

lr.score(X_test,y_test)

predicted = lr.predict(X_test)
predicted

data1 = pd.DataFrame({'Actual': y_test, 'Predicted' : predicted})
data1

from sklearn import metrics
import math
print('Mean Absolute Error:', metrics.mean_absolute_error(y_test,predicted))
print('Mean Squared Error:', metrics.mean_squared_error(y_test,predicted))
print('Root Mean Squared Error:', math.sqrt(metrics.mean_squared_error(y_test,predicted)))

graph = data1.head(20)
graph.plot(kind='bar')



"""**KNN**"""

# KNN Regression
knn = KNeighborsRegressor(n_neighbors=2)
knn.fit(X_train, y_train)
knn_prediction = knn.predict(X_test)
knn_metrics =evaluate_model(y_test, knn_prediction, "KNN")
combined_metrics.append(knn_metrics)
knn_metrics

# KNN Regression
clfknn = KNeighborsRegressor(n_neighbors=2)
clfknn.fit(X_train, y_train)

confidenceknn = clfknn.score(X_test, y_test)
print('The KNN confidence is {}'.format(confidenceknn))

forecast_set = clfknn .predict(X_test)
new_data['Forecast'] = np.nan
forecast_set

data2 = pd.DataFrame({'Actual': y_test, 'Predicted' : forecast_set})
data2

print('Mean Absolute Error:', metrics.mean_absolute_error(y_test,forecast_set))
print('Mean Squared Error:', metrics.mean_squared_error(y_test,forecast_set))
print('Root Mean Squared Error:', math.sqrt(metrics.mean_squared_error(y_test,forecast_set)))





"""### Models Summary"""

from functools import reduce

# Perform as-of merges
_combined_metrics = reduce(lambda left, right:
             left.join(right),
             combined_metrics)
_combined_metrics

_combined_metrics.T

"""## Evaluations Summary"""

import seaborn as sns
import matplotlib.pyplot as plt

for col in _combined_metrics.T.columns:
    series = _combined_metrics.T
    df = pd.DataFrame(series[col].sort_values(ascending = False))
    plt.figure(figsize=(12, 5))
    plt.style.use('default')
    plt.barh(df.index,df[col])
    plt.title(col)














