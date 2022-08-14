import numpy as np
import pandas as pd
import hvplot.pandas  # noqa

#For Monte Carlo
import random

#Visualization
import holoviews as hv

from tqdm import tqdm

#Historical Data
import investpy

stocks = ['AAPL', 'NFLX', 'TSLA', 'GOOG', 'TWTR', 'AMZN', 'SNAP', 'BABA']

begin_date = "01/01/2020"
end_date = "14/08/2022"

def generate_stock_returns(stocks_list, begin_date, end_date):
    
    prices = pd.DataFrame()
    
    for stock in stocks_list:
        df_ = investpy.get_stock_historical_data(stock=stock,
                                                 country='United States',
                                                from_date=begin_date,
                                                to_date=end_date).Close
        df_.rename(stock, inplace=True)                                             
        df_.columns = [stock]
        prices = pd.concat([prices, df_],axis=1)
        prices.index.name = "Date"
    return prices

def portfolio_metrics(weights, index):
    
    '''
    This function generates the relative performance metrics that will be reported and will be used
    to find the optimal weights.
    
    Parameters:
    weights: initialized weights or optimal weights for performance reporting
    
    '''   
    
    rp = (returns.mean()*252)@weights 
    port_var = weights@(cov*252)@weights
    sharpe = (rp-rf)/np.sqrt(port_var)
    df = pd.DataFrame({"Expected Return": rp,
                       "Portfolio Variance":port_var,
                       'Portfolio Std': np.sqrt(port_var),
                       'Sharpe Ratio': sharpe}, index=[index])
    return df

def optimal_portfolio_weights(weights):
    df = pd.DataFrame({"Stock": stocks,
                       "Weights": weights})
    df.Weights = df.Weights.map(lambda x: '{:.2%}'.format(x))
    return df

prices = generate_stock_returns(stocks, begin_date, end_date)
# print(prices)

returns = prices.pct_change()
# print(returns)

cov = returns.cov()
# print(cov)

np.random.seed(10) #for replicability
weights = np.random.random(len(stocks))
weights /= np.sum(weights)
# print(weights)

rp = (returns.mean()*252)@weights 
# print(rp)

# Portfolio Variance
port_var = weights@(cov*252)@weights 
# print(port_var)

# Sharpe Ratio
rf = 0.02 #risk-free rate
sharpe = (rp-rf)/np.sqrt(port_var)
# print(sharpe)

np.random.seed(42)
portfolios = pd.DataFrame(columns=[*stocks, "Expected Return","Portfolio Variance", "Portfolio Std", "Sharpe Ratio"])

for i in range(100):
    weights = np.random.random(len(stocks))
    weights /= np.sum(weights)
    portfolios.loc[i, stocks] = weights
    metrics = portfolio_metrics(weights,i)
    portfolios.loc[i, ["Expected Return","Portfolio Variance", "Portfolio Std", "Sharpe Ratio"]] = \
    metrics.loc[i,["Expected Return","Portfolio Variance", "Portfolio Std", "Sharpe Ratio"]]
 
optimal_portfolio = portfolios[portfolios["Sharpe Ratio"]==portfolios["Sharpe Ratio"].max()].T
opt_weights = portfolios[portfolios["Sharpe Ratio"]==portfolios["Sharpe Ratio"].max()].to_numpy()[0][0:len(stocks)]
print(optimal_portfolio_weights(opt_weights))
