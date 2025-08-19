#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dash import html, dcc
import plotly.express as px
from the_data.sample_data import data

initial_fig = px.choropleth(
    data,
    locations="ISO_Code",
    color="Attractiveness",
    hover_name="Country",
    color_continuous_scale=px.colors.sequential.Plasma
)
initial_fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})

layout = html.Div([
    html.H1("The First Automatic Global Economic Intelligence Tool", style={'textAlign': 'center'}),
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.A("Map", href="/", style={'margin-right': '20px'}),
        html.A("Comparator", href="/compare")
    ], style={'textAlign': 'center', 'margin-bottom': '30px'}),
    dcc.Graph(id='map', figure=initial_fig, style={'display': 'none'}),
    html.Div(id='page-content')
])

