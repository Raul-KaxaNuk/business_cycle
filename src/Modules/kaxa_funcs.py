# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 20:31:15 2023

@author: edgar
"""

#%%

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fredapi import Fred

#statsmodels
import statsmodels.api as sm 

#linear algebra
from scipy.linalg import toeplitz

#%%

def wrangle(path):
    
    df = pd.read_excel(path)
    
    df.set_index(df.columns[0], inplace = True)
    
    df.index = pd.to_datetime(df.index)
    
    df.index.name = 'Date'
    
    return df

#%%

def get_fred_data(
        path: str
        ):
    
    fred_key= '0174cb93931388a2bf305663e4117fd3'

    fred = Fred(api_key = fred_key)
    
    features = pd.read_excel(path)
    
    df_concat = pd.DataFrame()
    
    for serie, ticker, bol in zip(features['series'], features['tickers'], features['status']):
        
        if bol:
        
            df = pd.Series(
                fred.get_series(ticker), 
                name = serie
                )
            
            df = df.resample('M').last()
            
            df_concat = pd.concat([
                df_concat, 
                df
                ], 
                axis = 1)
        
        else:
            
            pass
    
    df_concat.index = pd.to_datetime(df_concat.index)
    df_concat = df_concat.sort_index()
    
    return df_concat

#%%

def get_index_inputs(
        y: pd.Series(),
        x: pd.DataFrame()
        ):
    
    y = y.iloc[1:]
    
    x = x.pct_change(1).dropna()
    
    model = sm.OLS(y,x)
    
    results = model.fit()
    
    coefs = results.params
    
    r2 = results.rsquared_adj
    
    fitted = results.fittedvalues
    
    return coefs, r2, fitted
    

#%%

def get_index_inputs_gls(
        y: pd.Series(),
        x: pd.DataFrame()
        ):
    
    ols_resids = sm.OLS(y, x).fit().resid

    y_gls = ols_resids

    x_gls = ols_resids.shift(1)

    res_fit = sm.OLS(y_gls, x_gls).fit()

    rho = res_fit.params[0]

    order = toeplitz(range(len(ols_resids)))

    sigma = rho**order

    gls_model = sm.GLS(y, x, sigma=sigma)
    
    gls_results = gls_model.fit()
    
    print(gls_results.summary())

#%%

def detrending(
        y: pd.Series(),
        ):
    
    Y = y
    
    trend = pd.Series(np.arange(1, len(Y)+1), index = Y.index)
    
    X1 = pd.DataFrame(
        {
            "trend" : trend
         }
        )
    
    X2 = pd.DataFrame(
        {
            "trend" : trend,
            "trend_sq" : trend**2
         }
        )
    
    X3 = pd.DataFrame(
        {
            "trend" : trend,
            "trend_sq" : trend**2,
            "trend_cb" : trend**3
         }
        )
    
    model1 = sm.OLS(
        Y,
        sm.add_constant(X1)
        )
    
    results1 = model1.fit()
    
    model2 = sm.OLS(
        Y,
        sm.add_constant(X2)
        )
    
    results2 = model2.fit()
    
    model3 = sm.OLS(
        Y,
        sm.add_constant(X3)
        )
    
    results3 = model3.fit()
    
    if results1.aic <= results2.aic and results1.aic <= results3.aic:
        print(results1.summary())
        return results1.resid
    
    elif results2.aic <= results1.aic and results2.aic <= results3.aic:
        print(results2.summary())
        return results2.resid
    
    else:
        print(results3.summary())
        return results3.resid
        
#%%

def yields_calculation(group):
    if len(group) > 1:
        return ((group.iloc[-1] / group.iloc[0]))
    else:
        return np.nan