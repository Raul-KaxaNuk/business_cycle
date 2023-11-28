# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 18:15:43 2023

@author: edgar
"""
#%%

import pandas as pd
import matplotlib.pyplot as plt

#kaxamodules
from src.Modules import kaxa_funcs as kf

#statsmodels
import statsmodels.api as sm
import statsmodels.tsa.stattools as sts
import statsmodels.stats.stattools as sss
import statsmodels.stats.diagnostic as ssd

#linear algebra

#%%

#call data for leading features
lead_df = kf.get_fred_data('inputs/leading_features.xlsx')

#%%

#call data for coincident features
coin_df = kf.get_fred_data('inputs/coincident_features.xlsx')

#%%

#call data for lagging features
lag_df = kf.get_fred_data('inputs/lagging_features.xlsx')

lag_df['inflation'] = lag_df['cpi'].pct_change(12)*100

#%%

#call the benchmark
bench_df = kf.get_fred_data('inputs/dependent_features.xlsx')

#%%

#dropnans for the benchmark
dep_df = bench_df.dropna()

#%%

#calculate the gdp gap
dep_df['gdp_gap'] = (dep_df['gdp'].div(dep_df['potential_gdp']) - 1)*100

#lets see the objective variable
dep_df['gdp_gap'].plot()

#lets see if it is stationary
sts.adfuller(
    dep_df['gdp_gap'], 
    autolag = "AIC"
    )

#%%

#dataframe for leading features without nans
df1 = pd.concat([dep_df['gdp_gap'], lead_df], axis = 1)\
    .dropna()

#dataframe for coincident features without nans
df2 = pd.concat([dep_df['gdp_gap'], coin_df], axis = 1)\
    .dropna()

#dataframe for lagging features without nans
df3 = pd.concat([dep_df['gdp_gap'], lag_df], axis = 1)\
    .dropna()

#%%

#correlations
cor_1 = df1.corr()
cor_dif_1 = df1.pct_change(1).corr()

cor_2 = df2.corr()
cor_dif_2 = df2.pct_change(1).corr()

cor_3 = df3.corr()
cor_dif_3 = df3.pct_change(1).corr()

#%%

#our endogenous variables
Y = dep_df['gdp_gap']

#%%

#leading exogenous
X1 = df1.drop(columns=['gdp_gap'])\
    .dropna()

#coincident exogenous
X2 = df2.drop(columns=['gdp_gap', 'personal_consumption'])\
    .dropna()

#lagging exogenous
X3 = df3.drop(columns=['gdp_gap', 'cpi', 'auto_inventory_to_sales'])\
    .dropna()

#%%

X3['inflation_lag_1'] = X3['inflation'].shift(1)

X3['average_hourly_earnings_total_lag_1'] = X3['average_hourly_earnings_total'].shift(1)

X3['retail_inventory_to_sales_lag_1'] = X3['retail_inventory_to_sales'].shift(1)

#%%
#resample so all datasets have the same time spam
start = pd.to_datetime(df1.index[0])

#Y resampling
Y = Y[Y.index >= start]

#X resampling
X2 = X2[X2.index >= start]

#X resampling
X3 = X3[X3.index >= start]

#%%

#lets do the first regression

model_1 = sm.OLS(
    Y, 
    sm.add_constant(X1)
    )

results_1 = model_1.fit()

print(results_1.summary())

#%%

#ploteemos

Y.plot()

results_1.fittedvalues.plot()

#%%

#hagamos pruebas

dw_1 = sss.durbin_watson(
    results_1.resid, 
    axis=0
    )

bp_1 = ssd.het_breuschpagan(
    results_1.resid, 
    sm.add_constant(X1),
    robust=True
    )

#%%

plt.scatter(
    results_1.fittedvalues, 
    results_1.resid
    )

#%%

#lets do the first regression

model_2 = sm.OLS(
    Y, 
    sm.add_constant(X2)
    )

results_2 = model_2.fit()

print(results_2.summary())

#%%

#ploteemos

Y.plot()

results_2.fittedvalues.plot()

#%%

#hagamos pruebas

dw_2 = sss.durbin_watson(
    results_2.resid, 
    axis=0
    )

bp_2 = ssd.het_breuschpagan(
    results_2.resid, 
    sm.add_constant(X2), 
    robust=True
    )

#%%

plt.scatter(
    results_2.fittedvalues, 
    results_2.resid
    )

#%%

#lets do the first regression

model_3 = sm.OLS(
    Y, 
    sm.add_constant(X3), 
    missing = 'drop')

results_3 = model_3.fit()

print(results_3.summary())

#%%

#ploteemos

Y.plot()

results_3.fittedvalues.plot()

#%%

#hagamos pruebas

dw_3 = sss.durbin_watson(
    results_3.resid, 
    axis=0
    )

bp_3 = ssd.het_breuschpagan(
    results_3.resid, 
    sm.add_constant(X3.dropna()), 
    robust=True
    )

#%%

plt.scatter(
    results_3.fittedvalues, 
    results_3.resid
    )

#%%

Y.plot()

results_1.fittedvalues.plot()

results_2.fittedvalues.plot()

results_3.fittedvalues.plot()

#%%

f_1 = results_1.fittedvalues

f_2 = results_2.fittedvalues

f_3 = results_3.fittedvalues

#%%

r2_1 = results_1.rsquared_adj

r2_2 = results_2.rsquared_adj

r2_3 = results_3.rsquared_adj

sum_r2 = r2_1 + r2_2 + r2_3

#%%

bci = (r2_1/sum_r2)*f_1 + (r2_2/sum_r2)*f_2 + (r2_3/sum_r2)*f_3

#%%

resids_bci = Y - bci

#%%

Y.plot()

bci.plot()
