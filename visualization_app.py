# This is the main body of the app, containing the generic logic concerning the tabs, as well as the selected-player and menu functionality
# The imports include the tab-pages as well as the graphing libraries

from viz_app.main import app, dataframes, exclude_columns
from viz_app.config import player_tables
from viz_app.data import get_player_data
from viz_app.tabs import explore, search, compare
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import plotly.graph_objs as go

import plotly.express as px
from dash import html, dcc, ctx

# Default theme included in the example app
theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

# Some custom styling for the tabs
tab_style = {
    "border-style": "solid",
    "border": "none",
    "border-radius": "3px",
    "border-bottom": "1px black"
}

# More styling, specific to the selected tab
selected_tab_style = {
    "border-style": "solid",
    "border": "none",
    "border-radius": "3px",
    "border-bottom": "1px black",
    "background": "#f4f4f4"
}

# Here the structure of the pages starts. The layout of the app is defined within the Div below.
# We first add a page wide storage that saves the users selection of players (dcc.Store(id='selected-players'))
# The next Div contains the title within the app, as well as the tab buttons using the dcc Tabs component
# Following the tabs is the player selection. Those three elements form the side menu which has a width of 3 columns (out of 12)
# The last element is the tab container, which shows the tabs' contents using a callback
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
                    dcc.Tab(label='Search', value='tab-search', selected_style=selected_tab_style, style=tab_style),
                    dcc.Tab(label='Compare', value='tab-compare', selected_style=selected_tab_style, style=tab_style)
                ], vertical=True, mobile_breakpoint=None)], style={'background': 'white'}),
            html.Div([
                html.H3('Selected', style={'border-bottom': '1px', 'background': '#D5D6EC', 'color': '#fafafa'}),
                html.Ul(id='player-selection', children=[], style={'min-height': '50px'}),
            ], style={'background': 'white', 'margin-top': '20px'})], className='three columns'),

            html.Div(id='tab-view', children=[
                html.H2('Explore', style={'text-align': 'center'}),
                explore.layout
            ], className='nine columns'),
        ])

    # This callback allows us to switch between tabs using the tab buttons. The page is reloaded dynamically by
    # dash, allowing us to save the menu data in a page specific storage instead of a session.
    @app.callback(
        Output('tab-view', 'children'),
        Input('tabs-select', 'value'))
    def change_tab(tab):
        if tab == 'tab-explore':
            return [html.H2('Explore', style={'text-align': 'center'}), explore.layout]
        elif tab == 'tab-search':
            return [html.H2('Search', style={'text-align': 'center'}), search.layout]
        elif tab == 'tab-compare':
            return [html.H2('Compare', style={'text-align': 'center'}), compare.layout]

    # The second callback is a generic callback which renders the contents of the selected players to the menu.
    # it reacts to changes made in the intermediate variable, allowing us to reduce code duplication between tabs
    # The n_clicks property is used in the third callback
    @app.callback(
        Output('player-selection', 'children'),
        Input('selected-players', 'value'))
    def update_selection(players):
        return [html.Li(player, id={"type": "player-list-item", "index": player}, n_clicks=0) for player in players]


    # The third callback allows us to delete players from the selection using a somewhat hacky solution with a
    # n_clicks property on the list elements. The change in selected-players triggers the previous callback, updating
    # the visual accordingly.
    @app.callback(
        Output('selected-players',  'value', allow_duplicate=True),
        Input({"type": "player-list-item", "index": ALL}, 'n_clicks'),
        State('selected-players', 'value'),
        prevent_initial_call=True)
    def remove_from_selection(player_clicks, players):
        players = [x[1] for x in zip(player_clicks, players) if x[0] == 0]
        return players

    # Starting the app
    app.run_server(debug=False, dev_tools_ui=False)



