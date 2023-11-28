# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 10:29:10 2023

@author: edgar
"""

#%%

#statsmodels

#kaxamodules
from src.Modules import kaxa_funcs as kf

#plotly

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

#store data

lead_df.to_excel('data/lead_inds.xlsx')

coin_df.to_excel('data/coin_inds.xlsx')

lag_df.to_excel('data/lag_inds.xlsx')

bench_df.to_excel('data/bench_inds.xlsx')

#%%