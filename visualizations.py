# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 10:24:20 2023

@author: edgar
"""

#%%

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fredapi import Fred

#statsmodels
import statsmodels.api as sm 

#kaxamodules
import src.Modules.kaxa_funcs as kf
import src.Modules.kaxa_plots as kp

#plotly
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go

#%%

#call data for leading features
lead_df = kf.wrangle('data/lead_inds.xlsx')

#%%

#call data for coincident features
coin_df = kf.wrangle('data/coin_inds.xlsx')

#%%

#call data for lagging features
lag_df = kf.wrangle('data/lag_inds.xlsx')

#%%

#call the benchmark
bench_df = kf.wrangle('data/bench_inds.xlsx')

#%%

#dropnans for the benchmark
df = bench_df.dropna()

#%%

#calculate the gdp gap
df['gdp_gap'] = (df['gdp'].div(df['potential_gdp']) - 1).mul(100)

#calculate real economic growth
df['economic_growth'] = df['gdp'].pct_change(1).mul(100)

#calculate potential economic growth
df['potential_economic_growth'] = df['potential_gdp'].pct_change(1).mul(100)

#calculate growth gap
df['growth_gap'] = df['economic_growth'] - df['potential_economic_growth']

#%%

#make the categorization
df["Phase"] = "Recovery"
df.loc[(df["gdp_gap"] > 0) & (df["growth_gap"] > 0), "Phase"] = "Expansion"
df.loc[(df["gdp_gap"] > 0) & (df["growth_gap"] < 0), "Phase"] = "Slowdown"
df.loc[(df["gdp_gap"] < 0) & (df["growth_gap"] < 0), "Phase"] = "Contraction"

#%%

#dataframe for leading features without nans
df1 = lead_df.dropna()

#dataframe for coincident features without nans
df2 = coin_df.dropna()

#dataframe for lagging features without nans
df3 = lag_df.dropna()

#%%

df3['inflation'] = df3['cpi'].pct_change(12).mul(100)

#%%

df_spy = pd.read_csv('inputs/SPY.csv').set_index('Date')

df_spy.index = pd.to_datetime(df_spy.index)

df4 = pd.concat([df, df_spy['Adj Close']], axis = 1)

#%%

kp.time_series_plot(df, df_spy['Adj Close'], title = 'GDP vs SPY', file = 'gdp_vs_spy')

#%%
for i in df1.columns:
    
    kp.time_series_plot(df, df1[i], title = f'GDP vs {i}', file = f'gdp_vs_{i}')

#%%

for i in df2.columns:
    
    kp.time_series_plot(df, df2[i], title = f'GDP vs {i}', file = f'gdp_vs_{i}')
    
#%%

for i in df3.columns:
    
    kp.time_series_plot(df, df3[i], title = f'GDP vs {i}', file = f'gdp_vs_{i}')

#%%
kp.time_series_plot(df, df1['2_years_yield'], title = 'GDP vs 2YY', file = 'gdp_vs_2yy', stand = False)
kp.time_series_plot(df, df1['reference_interest_rate'], title = 'GDP vs FFER', file = 'gdp_vs_ffer', stand = False)

#%%

kp.time_series_plot(
    df, 
    df1['reference_interest_rate'], 
    df1['2_years_yield'],
    title = 'GDP vs FFER vs 2YY', 
    file = 'gdp_vs_ffervs2yy', 
    stand = False
    )
