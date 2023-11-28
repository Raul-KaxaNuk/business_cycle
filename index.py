# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 16:09:19 2023

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
import plotly.graph_objs as go

#%%

#call the benchmark
df = kf.get_fred_data('inputs/dependent_features.xlsx')

#%%

df['gdp_gap'] = (df['gdp'].div(df['potential_gdp']) - 1).mul(100)

df['economic_growth'] = df['gdp'].pct_change(1).mul(100)

df['annual_economic_growth'] = df['gdp'].pct_change(12).mul(100)

df['potential_economic_growth'] = df['potential_gdp'].pct_change(1).mul(100)

df['trend_economic_growth'] = ((df['gdp'].dropna()[-1]/df['gdp'].dropna()[0])**(1/len(df['gdp'].dropna())) - 1) * 100

#%%

df['growth_gap'] = df['economic_growth'] - df['potential_economic_growth']

df['trend_gap'] = df['economic_growth'] - df['trend_economic_growth']

#%%

df.dropna(inplace = True)

#%%

df['gdp_gap'].plot()

#%%

df['economic_growth_derivative'] = df['economic_growth'].pct_change(1).mul(100)

#%%

df["Phase1"] = "Recovery"
df.loc[(df["gdp_gap"] > 0) & (df["growth_gap"] > 0), "Phase1"] = "Expansion"
df.loc[(df["gdp_gap"] > 0) & (df["growth_gap"] < 0), "Phase1"] = "Slowdown"
df.loc[(df["gdp_gap"] < 0) & (df["growth_gap"] < 0), "Phase1"] = "Contraction"

#%%

fig1 = px.bar(df, x=df.index, y="gdp_gap", color="Phase1")

pio.write_html(fig1, 'outputs/bars1.html');

#%%

df["Phase2"] = "Recovery"
df.loc[(df["gdp_gap"] > 0) & (df["trend_gap"] > 0), "Phase2"] = "Expansion"
df.loc[(df["gdp_gap"] > 0) & (df["trend_gap"] < 0), "Phase2"] = "Slowdown"
df.loc[(df["gdp_gap"] < 0) & (df["trend_gap"] < 0), "Phase2"] = "Contraction"

#%%

fig2 = px.bar(df, x=df.index, y="gdp_gap", color="Phase2")

pio.write_html(fig2, 'outputs/bars2.html');

#%%

df_spy = pd.read_csv('inputs/SPY.csv').set_index('Date')

df_spy.index = pd.to_datetime(df_spy.index)

df_spy = df_spy.resample('Q').last()

df_spy['Adj Close'].plot()

#%%

df_spy["adj_close_norm"] = df_spy['Adj Close']/df_spy['Adj Close'][0]

df_spy['adj_close_norm'].plot()

#%%

df_spy['adj_close_detrend'] = kf.detrending(df_spy['adj_close_norm'])

#%%

df_spy['adj_close_detrend'].plot()

#%%

fig3 = px.line(df_spy, x=df_spy.index, y='adj_close_detrend')

pio.write_html(fig3, 'outputs/line1.html');

#%%

start = pd.to_datetime(df_spy.index[0])

df1 = df[df.index >= start]

fig1 = px.bar(df1, x=df1.index, y="gdp_gap", color="Phase1")

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
pio.write_html(fig, 'outputs/plot1.html');