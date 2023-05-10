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

if __name__ == '__main__':

    app.layout = html.Div(
        id="app-container",
        children=[
            html.Div([
                html.H1('Soccer Scout Dashboard', style={'textAlign': 'center'}),
            ]),

            dcc.Tabs([
                search.layout,
                explore.layout
            ]),
        ])

    app.run_server(debug=False, dev_tools_ui=False)
