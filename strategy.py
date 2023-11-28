# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 09:52:25 2023

@author: edgar
"""
#%%

import pandas as pd
import numpy as np

#statsmodels

#kaxamodules
from src.Modules import kaxa_funcs as kf

#plotly
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go

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

sell_signs1 = np.where(
    (df['Phase'] == "Slowdown") & 
    (df['Phase'].shift(1) == "Expansion") & 
    (df['Phase'].shift(2) == "Expansion"), 
    -1, 
    0
    )

sell_signs2 = np.where(
    (df['Phase'] == "Contraction") & 
    (df['Phase'].shift(1) == "Recovery") & 
    (df['Phase'].shift(2) == "Recovery"), 
    -1, 
    0
    )

buy_signs1 = np.where(
    (df['Phase'] == "Recovery") & 
    (df['Phase'].shift(1) == "Contraction") & 
    (df['Phase'].shift(2) == "Contraction"), 
    1, 
    0)

buy_signs2 = np.where(
    (df['Phase'] == "Expansion") & 
    (df['Phase'].shift(1) == "Slowdown") & 
    (df['Phase'].shift(2) == "Slowdown"), 
    1, 
    0)

signs = sell_signs1 + sell_signs2 + buy_signs1 + buy_signs2

df['strategy_sign'] = signs

#%%

df['strategy'] = "None"
df.loc[df['strategy_sign'] == -1, "strategy"] = "Sell"
df.loc[df['strategy_sign'] == 1, "strategy"] = "Buy"

#%%

fig1 = px.bar(df, x=df.index, y="gdp_gap", color='strategy')

pio.write_html(fig1, 'outputs/strat.html');

#%%

df_spy_daily = pd.read_csv('inputs/SPY.csv').set_index('Date')

df_spy_daily.index = pd.to_datetime(df_spy_daily.index)

df_spy = df_spy_daily.resample('Q').last()

df_spy['Adj Close'].plot()

#%%

df_spy["adj_close_norm"] = df_spy['Adj Close']/df_spy['Adj Close'][0]

#%%

df_spy['adj_close_detrend'] = kf.detrending(df_spy['adj_close_norm'])

#%%

start = pd.to_datetime(df_spy.index[0])

df1 = df[df.index >= start]

fig1 = px.bar(df1, x=df1.index, y="gdp_gap", color='strategy')

fig3 = px.line(df_spy, x=df_spy.index, y='adj_close_detrend', line_shape='linear')

fig3.data[0].update(line=dict(color='black'))

# Crear una nueva figura
fig = go.Figure()

# Agregar la gráfica de barras a la figura
for trace in fig1.data:
    fig.add_trace(trace)

# Agregar la gráfica de línea a la figura
for trace in fig3.data:
    fig.add_trace(trace)

# Actualizar el diseño de la gráfica
fig.update_layout(title_text="GDP Gap vs SPY")

# Mostrar la gráfica
pio.write_html(fig, 'outputs/plot_strat.html');
    
#%%

start = pd.to_datetime(df_spy.index[0])

df = df[df.index >= start]

#%%

df['stock_cum'] = 0

stocks = 1

for i in range(1, len(df)):
    
    df.iloc[i, 9] = stocks*df.iloc[i, 7] + df.iloc[i-1, 9]
    
    if df.iloc[i, 9] < 0:
        df.iloc[i, 9] = df.iloc[i, 9] + stocks
    
    else:
        pass
    
    if df.iloc[i, 9] > 1:
        df.iloc[i, 9] = df.iloc[i, 9] - stocks
    
    else:
        pass

#%%

df_strat = pd.concat([df_spy_daily['Adj Close'], df['stock_cum']], axis = 1).rename(columns={'Adj Close':'adj_close'})

df_strat = df_strat.fillna(method = 'bfill').dropna()

#%%

df_strat['stock_vol'] = df_strat['adj_close']*df_strat['stock_cum']

df_strat['stock_vol'] = df_strat['stock_vol'].replace(0, np.nan)

#%%

df_strat['port_ret'] = np.nan

for i in range(1, len(df_strat)):
    
    if not np.isnan(df_strat.iloc[i, 2]):
        df_strat.iloc[i, 3] = (df_strat.iloc[i, 2]/df_strat.iloc[i-1, 2])-1
    
    else:
        pass
    
#df_strat['port_ret'] = df_strat['port_ret'].fillna(method='ffill')

#%%

df_strat['group'] = (df_strat['stock_vol'].isnull() & df_strat['stock_vol'].shift(fill_value=False)).cumsum()

for i in range(len(df_strat)):
    
    if pd.isna(df_strat.iloc[i, 2]):
        df_strat.iloc[i, 4] = np.nan
    else:
        pass

#%%

yields = df_strat.groupby('group')['stock_vol'].apply(kf.yields_calculation)

#%%

strat_return = yields.prod()

bench_yield = df_strat['adj_close'].iloc[-1]/df_strat['adj_close'].iloc[0]
