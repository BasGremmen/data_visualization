from viz_app.main import app, dataframes, exclude_columns
from viz_app.config import player_tables
from viz_app.data import get_player_data
from viz_app.tabs import explore, search
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go

import plotly.express as px
from dash import html, dcc

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

tab_style = {
    "border-style": "solid",
    "border": "1px 0 0 0",
    "border-color": "grey"
}

selected_tab_style = {
    "border-style": "solid",
    "border": "1px 0 0 0",
    "border-color": "grey"
}

if __name__ == '__main__':
    app.layout = html.Div(
        id="app-container",
        children=[
            dcc.Store(id='selected-players'),
            html.Div(children=[
                html.H1('Scoutlier', style={'text-align': 'center'}),
                html.Div([
                dcc.Tabs(id="tabs-select", value='tab-explore', children=[
                    dcc.Tab(label='Explore', value='tab-explore', selected_style=selected_tab_style, style=tab_style),
                    dcc.Tab(label='Search', value='tab-search', selected_style=selected_tab_style, style=tab_style)
                ], vertical=True, mobile_breakpoint=None)])], className='three columns'),

            html.Div(id='tab-view', children=[
                explore.layout
            ], className='nine columns'),
        ])


    @app.callback(
        Output('tab-view', 'children'),
        Input('tabs-select', 'value'))
    def change_tab(tab):
        if tab == 'tab-explore':
            return explore.layout
        elif tab == 'tab-search':
            return search.layout


    app.run_server(debug=False, dev_tools_ui=False)
