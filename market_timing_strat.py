# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 09:52:25 2023

@author: edgar
"""
# %%

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# statsmodels

# kaxamodules
from src.Modules import kaxa_funcs as kf

# plotly
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go

# %%

# call the benchmark
bench_df = kf.wrangle('data/bench_inds.xlsx')

# %%

# dropnans for the benchmark
df = bench_df.dropna()

# %%

# calculate the gdp gap
df['gdp_gap'] = (df['gdp'].div(df['potential_gdp']) - 1)#.mul(100)

# calculate real economic growth
df['economic_growth'] = df['gdp'].pct_change()#.mul(100)

# calculate potential economic growth
df['potential_economic_growth'] = df['potential_gdp'].pct_change()#.mul(100)

# calculate growth gap
df['growth_gap'] = df['economic_growth'] - df['potential_economic_growth']

# %%

# make the categorization
df["Phase"] = "Recovery"
df.loc[(df["gdp_gap"] > 0) & (df["growth_gap"] > 0), "Phase"] = "Expansion"
df.loc[(df["gdp_gap"] > 0) & (df["growth_gap"] < 0), "Phase"] = "Slowdown"
df.loc[(df["gdp_gap"] < 0) & (df["growth_gap"] < 0), "Phase"] = "Contraction"

# %%

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
df['strategy_sign_lagg'] = df['strategy_sign'].shift()

# %%

df['strategy'] = "None"
df.loc[df['strategy_sign'] == -1, "strategy"] = "Sell"
df.loc[df['strategy_sign'] == 1, "strategy"] = "Buy"

# %%

# fig1 = px.bar(df, x=df.index, y="gdp_gap", color='strategy')
#
# pio.write_html(fig1, 'outputs/strat.html');

# %%

df_spy_daily = pd.read_csv('inputs/SPY.csv').set_index('Date')

df_spy_daily.index = pd.to_datetime(df_spy_daily.index)

df_spy = df_spy_daily.resample('Q').last()

df_spy['Adj Close'].plot()
plt.show()

# %%

start = pd.to_datetime(df_spy.index[0])

df = df[df.index >= start]

# %%
# 'strategy_sign'
strat_df = df[['Phase', 'strategy_sign_lagg','strategy']]

strat_df['stock_cum'] = 0

#%%

strat_df['buy_stocks'] = np.where((strat_df['strategy_sign_lagg'] == 1), 4, 0)

strat_df['total_stocks'] = strat_df['buy_stocks'].cumsum()


#%%

total_shares = strat_df['buy_stocks'].sum()

shares_per_year = strat_df['buy_stocks'].sum()/((strat_df.index[-1]-strat_df.index[0]).days/365)

print(f'Compras {shares_per_year:.2f} por año en {((strat_df.index[-1]-strat_df.index[0]).days/365): .1f} años, para un total de {total_shares}')

#%%

spy_strat = pd.concat([df_spy_daily['Adj Close'], strat_df[['buy_stocks','total_stocks', 'strategy_sign_lagg']]], axis = 1)
spy_strat['total_stocks'] = spy_strat['total_stocks'].fillna(method = 'ffill')
spy_strat['buy_stocks'] = spy_strat['buy_stocks'].fillna(0)
spy_strat['strategy_sign_lagg'] = spy_strat['strategy_sign_lagg'].fillna(0)
"1997-07-31"
spy_strat['Adj Close'] = spy_strat['Adj Close'].fillna(method='bfill')
spy_strat.dropna(inplace = True)

spy_strat['portfolio_value'] = spy_strat['total_stocks'] * spy_strat['Adj Close']


#%%
portfolio_df = spy_strat.loc[spy_strat['strategy_sign_lagg']==1]
initial_investment = (portfolio_df['buy_stocks'] * portfolio_df['Adj Close']).sum()

ending_value = spy_strat.iloc[-1, 4]

total_ret = ending_value/initial_investment

an_ret = (total_ret ** (252/spy_strat.shape[0]))-1

print(f'total annual return: {an_ret: .4%}')

#%%

def string_formater(string):
    return str(string).split(' ')[0]

buy_stock_dates = pd.bdate_range(
    start=string_formater(spy_strat.index[0]),
    end= string_formater(spy_strat.index[-1]),
    freq= 'AS'
)

len(buy_stock_dates)

offset_dates = []
for date in buy_stock_dates:
    next_business_day = pd.bdate_range(date, periods=2, freq='BMS')[-1]
    offset_dates.append(next_business_day)

# offset_dates = [string_formater(i) for i in offset_dates]
# buy_stock_dates = pd.date_range(start=string_formater(spy_strat.index[0]),
#                                 end= string_formater(spy_strat.index[-1]),
#                                 periods=10)

shares_periodic = 10

spy_strat.loc[offset_dates, 'periodic_strat_signal'] = shares_periodic
spy_strat['periodic_strat_signal'] = spy_strat['periodic_strat_signal'].fillna(0)
spy_strat['periodic_strat_pf'] = spy_strat['periodic_strat_signal'].cumsum()
spy_strat['periodic_strat_pf'] = spy_strat['periodic_strat_pf'].fillna(method='ffill')

spy_strat['periodic_strat_portval'] = spy_strat['periodic_strat_pf'] * spy_strat['Adj Close']

per_spy = spy_strat.loc[spy_strat['periodic_strat_signal']==shares_periodic]
initial_investment_per = (per_spy['Adj Close'] * per_spy['periodic_strat_signal']).sum()

ending_value_per = spy_strat.iloc[-1, 7]

total_ret_per = ending_value_per/initial_investment_per

an_ret_per = (total_ret_per ** (252/spy_strat.shape[0]))-1


print(f'Edgar Strat annual return: {an_ret: .4%}')
print(f'Periodic Strat annual return: {an_ret_per: .4%}')


