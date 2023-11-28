# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 20:37:07 2023

@author: edgar
"""

#%%

import pandas as pd

#statsmodels

#kaxamodules
from src.Modules import kaxa_funcs as kf

#plotly
import plotly.express as px
import plotly.io as pio

#%%

#call data for leading features
lead_df = kf.get_fred_data('inputs/leading_features.xlsx')

#%%

#call data for coincident features
coin_df = kf.get_fred_data('inputs/coincident_features.xlsx')

#%%

#call data for lagging features
lag_df = kf.get_fred_data('inputs/lagging_features.xlsx')

#%%

#call the benchmark
bench_df = kf.get_fred_data('inputs/dependent_features.xlsx')

#%%

#dropnans for the benchmark
dep_df = bench_df.dropna()

#%%

#calculate the gdp gap
dep_df['gdp_gap'] = dep_df['gdp'].div(dep_df['potential_gdp']) - 1

dep_df['gdp_gap'].plot()

#%%

#dataframe for leading features without nans
df1 = pd.concat([dep_df['gdp_gap'], lead_df], axis = 1).dropna()

#dataframe for coincident features without nans
df2 = pd.concat([dep_df['gdp_gap'], coin_df], axis = 1).dropna()

#dataframe for lagging features without nans
df3 = pd.concat([dep_df['gdp_gap'], lag_df], axis = 1).dropna()

#%%

#our endogenous variables
Y = dep_df['gdp_gap']

#%%

#leading exogenous
X1 = df1.drop(columns=['gdp_gap', 'm1', 'm2', 'overtime']).dropna()

#coincident exogenous
X2 = df2.drop(columns=['gdp_gap']).dropna()

#lagging exogenous
X3 = df3.drop(columns=['gdp_gap']).dropna()

#%%

#resample so all datasets have the same time spam
start = pd.to_datetime('2006-04-30 00:00:00')

#Y resampling
Y = Y[Y.index >= start]

#X resampling
X2 = X2[X2.index >= start]

#%%

#now obtaining inputs for the leading index
alphas, r2_lead, fitted_lead = kf.get_index_inputs(Y, X1)

#obtaining inputs for the coincident indes
betas, r2_coin, fitted_coin = kf.get_index_inputs(Y, X2)

#obtaining inputs for the lagging inputs
deltas, r2_lag, fitted_lag = kf.get_index_inputs(Y, X3)

#%%

#Lets plot all the fitted values

Y.plot()

fitted_lead.plot()

fitted_coin.plot()

fitted_lag.plot()

#%%

#to obtain the first version of this index we are going to make a weighted average"
#weights are going to be the adjusted r2 of every regression

#sum of weihgts
sum_r2 = r2_lead + r2_coin + r2_lag

#the index primary inputs
lead_index = fitted_lead.mul(r2_lead/sum_r2)

coin_index = fitted_coin.mul(r2_coin/sum_r2)

lag_index = fitted_lag.mul(r2_lag/sum_r2)

#the index
bci_index = lead_index + coin_index + lag_index

#%%

Y.plot()

bci_index.plot()

#%%

df1 = lead_df.pct_change(1).dropna().drop(columns=['m1', 'm2', 'overtime'])

df2 = coin_df.pct_change(1).dropna()

df3 = lag_df.pct_change(1).dropna()

#%%

alphas_weight = alphas/alphas.sum()

betas_weight = betas/betas.sum()

deltas_weight = deltas/deltas.sum()

#%%

df_index_lead = df1.mul(alphas)

df_index_coin = df2.mul(betas)

df_index_lag = df3.mul(deltas)

#%%

index_lead = df_index_lead.sum(axis=1)

index_coin = df_index_coin.sum(axis=1)

index_lag = df_index_lag.sum(axis=1)

#%%

index_lead.plot()

index_coin[index_coin.index >= start].plot()

index_lag.plot()

#%%

bci_2 = index_lead.mul(r2_lead/sum_r2) + index_coin.mul(r2_coin/sum_r2) + index_lag.mul(r2_lag/sum_r2)

#%%

Y.plot()

bci_index.plot()

bci_2[bci_2.index >= start].plot()

#%%

bench_df = pd.concat([bench_df, bci_2], axis = 1).rename(columns={0:'bci'}).dropna()

bench_df['gdp_gap'] = bench_df['gdp'].div(bench_df['potential_gdp']) - 1

bench_df['economic_growth'] = bench_df['gdp'].pct_change(1).mul(100)

bench_df['potential_economic_growth'] = bench_df['potential_gdp'].pct_change(1).mul(100)

#%%

bench_df['growth_gap'] = (bench_df['economic_growth'] / bench_df['potential_economic_growth']) - 1

bench_df["Phase"] = "Recovery"
bench_df.loc[(bench_df["bci"] > 0) & (bench_df["growth_gap"] > 0), "Phase"] = "Expansion"
bench_df.loc[(bench_df["bci"] > 0) & (bench_df["growth_gap"] < 0), "Phase"] = "Slowdown"
bench_df.loc[(bench_df["bci"] < 0) & (bench_df["growth_gap"] < 0), "Phase"] = "Contraction"

#%%

fig = px.bar(bench_df, x=bench_df.index, y="gdp_gap", color="Phase")

pio.write_html(fig, 'outputs/bars_index.html');