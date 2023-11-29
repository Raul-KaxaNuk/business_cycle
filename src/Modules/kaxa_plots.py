# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 09:11:31 2023

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

#plotly
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go
from plotly.subplots import make_subplots

#%%

def time_series_plot(
        df,
        series,
        title = '',
        file = '',
        stand = True,
        ):
    
    start = pd.to_datetime(series.index[0])

    df1 = df[df.index >= start]
    
    if stand:
    
        series1 = kf.detrending(series)
        
        series_norm = series1
    
    else:
        
        series_norm = series
    
    offset1 = df1["gdp_gap"].mean()

    # Calcular los límites de los ejes
    y_axis1_max = max(df1["gdp_gap"].max() + offset1, -df1["gdp_gap"].min() - offset1)
    y_axis2_max = max(series_norm.max(), -series_norm.min())*1.05

    # Crear subgráficos con dos ejes y compartiendo el eje x
    fig = make_subplots(
        specs = [[{"secondary_y": True}]]
        )

    #barras
    for category, color in {'Contraction': 'red',
                            'Recovery': 'green',
                            'Expansion': 'blue',
                            'Slowdown': 'purple'}.items():
        
        subset = df1[df1["Phase"] == category]
        fig.add_trace(
            go.Bar(
                x = subset.index,
                y = subset["gdp_gap"],
                marker_color = color,
                name = category,
                legendgroup = category,  # Agrupar las leyendas por categoría
            ),
            secondary_y = False,
        )

    # Agregar línea al eje y secundario
    fig.add_trace(
        go.Scatter(
            x = series_norm.index, 
            y = series_norm, 
            mode = "lines", 
            line = dict(color = "black"), 
            name = series.name),
        secondary_y = True,
    )
    
    fig.update_layout(
        title_text=f'{title}',
        yaxis=dict(range=[-y_axis1_max, y_axis1_max]),
        yaxis2=dict(range=[-y_axis2_max, y_axis2_max]),
        legend=dict(orientation="h", yanchor="bottom", xanchor="center", y=-0.2, x=0.5)
    )

    # Actualizar el diseño de la gráfica
    fig.update_layout(title_text = f'{title}')

    # Mostrar la gráfica
    pio.write_html(fig, f'outputs/{file}.html')

#%%


if series_sec is not None:
    fig.add_trace(
        go.Scatter(
            x = series_sec.index, 
            y = series_sec, 
            mode = "lines", 
            line = dict(color = "yellow"), 
            name = series_sec.name),
        secondary_y = True,
    )