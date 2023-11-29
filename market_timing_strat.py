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

strat_df = df[['Phase', 'strategy_sign','strategy']]

strat_df['stock_cum'] = 0

#%%

strat_df['buy_stocks'] = np.where((strat_df['strategy_sign'] == 1), 1, 0)

strat_df['total_stocks'] = strat_df['buy_stocks'].cumsum()


#%%

total_shares = strat_df['buy_stocks'].sum()

shares_per_year = strat_df['buy_stocks'].sum()/((strat_df.index[-1]-strat_df.index[0]).days/365)

print(f'Compras {shares_per_year:.2f} por año en {((strat_df.index[-1]-strat_df.index[0]).days/365): .1f} años, para un total de {total_shares}')

#%%

df_spy_daily = pd.concat([df_spy_daily['Adj Close'], strat_df[['buy_stocks','total_stocks', 'strategy_sign']]], axis = 1)
df_spy_daily['total_stocks'] = df_spy_daily['total_stocks'].fillna(method = 'ffill')
df_spy_daily['buy_stocks'] = df_spy_daily['buy_stocks'].fillna(0)
df_spy_daily['strategy_sign'] = df_spy_daily['strategy_sign'].fillna(0)
"1997-07-31"
df_spy_daily['Adj Close'] = df_spy_daily['Adj Close'].fillna(method='bfill')
df_spy_daily.dropna(inplace = True)

df_spy_daily['portfolio_value'] = df_spy_daily['total_stocks'] * df_spy_daily['Adj Close']


#%%
initial_investment = df_spy_daily.loc[df_spy_daily['strategy_sign']==1, 'Adj Close'].sum()
ending_value = df_spy_daily.iloc[-1, 4]

total_ret = ending_value/initial_investment

an_ret = (total_ret ** (252/df_spy_daily.shape[0]))-1

print(f'total annual return: {an_ret: .4%}')

#%%

def string_formater(string):
    return str(string).split(' ')[0]
buy_stock_dates = pd.bdate_range(start=string_formater(df_spy_daily.index[0]),
                                end= string_formater(df_spy_daily.index[-1]),
                                freq= 'AS')
len(buy_stock_dates)

offset_dates = []
for date in buy_stock_dates:
    next_business_day = pd.bdate_range(date, periods=2, freq='BMS')[-1]
    offset_dates.append(next_business_day)

# offset_dates = [string_formater(i) for i in offset_dates]
# buy_stock_dates = pd.date_range(start=string_formater(df_spy_daily.index[0]),
#                                 end= string_formater(df_spy_daily.index[-1]),
#                                 periods=10)
df_spy_daily.loc[offset_dates, 'periodic_strat_signal'] = 1
df_spy_daily['periodic_strat_signal'] = df_spy_daily['periodic_strat_signal'].fillna(0)
df_spy_daily['periodic_strat_pf'] = df_spy_daily['periodic_strat_signal'].cumsum()
df_spy_daily['periodic_strat_pf'] = df_spy_daily['periodic_strat_pf'].fillna(method='ffill')

df_spy_daily['periodic_strat_portval'] = df_spy_daily['periodic_strat_pf'] * df_spy_daily['Adj Close']



initial_investment_per = df_spy_daily.loc[df_spy_daily['periodic_strat_signal']==1, 'Adj Close'].sum()
ending_value_per = df_spy_daily.iloc[-1, 7]

total_ret_per = ending_value_per/initial_investment_per

an_ret_per = (total_ret_per ** (252/df_spy_daily.shape[0]))-1


print(f'total annual return: {an_ret: .4%}')
print(f'total annual return: {an_ret_per: .4%}')


#%%




