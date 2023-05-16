# The imports here consist of basic dash functionality, some plotting as well as custom functions
from dash import callback, Input, Output, dcc, html, Dash, State
import plotly.graph_objs as go
import plotly.express as px

from viz_app.main import dataframes, exclude_columns
from viz_app.config import player_tables
import pandas as pd

# The compare view consists of multiple rows which contain 2 columns of width 6 (6/12)
# The first row contains the selects for dataset and feature and the second row contains the output using 2 graphs
# The contents of the feature select, as well as the graphs is done dynamically using callbacks
layout = dcc.Tab(label='Compare Players', children=[
    html.Div([
        html.Div([
            html.Label('Select Stat Category'),
            dcc.Dropdown(
                id='compare-stats-dropdown',
                options=[{'label': stat, 'value': stat} for stat in player_tables],
                style={'width': '100%'},
                value='player_defense'
            ),
        ], className='six columns'),

        html.Div([
            html.Label('Select Feature'),
            dcc.Dropdown(
                id='compare-feature-dropdown',
                style={'width': '100%'},
                multi=True
            ),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '10px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='compare-players-chart', clickData=None),
        ], className='six columns'),
        html.Div([
            dcc.Graph(id='compare-radar-chart'),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '10px'}),

])


# Our first callback updates the radar chart hwen either dataset changes, features changes, or player selection changes
@callback(
    Output('compare-radar-chart', 'figure'),
    Input('selected-players', 'value'),
    Input('compare-stats-dropdown', 'value'),
    Input('compare-feature-dropdown', 'value'))
def update_compare_radar_chart(players, selected_stat, selected_features):
    # Is no dataset is selected for whatever reason, return an empty figure
    if selected_stat is None:
        return go.Figure()

    # Copy the original dataframe to keep the original clean
    df = dataframes[selected_stat].copy()

    # Let's exclude some default columns that are not interesting within a radar
    features = df.columns.difference([*exclude_columns, 'club', 'position', 'age', 'player', 'team'])

    # if no features are selected, set the selected features to all features
    if selected_features is None:
        selected_features = features

    # this bit of code checks whether the values are valid, ignoring any invalid values. If the remaining number of
    # features is 0, we revert back to all features of the dataset
    selected_features = [x for x in selected_features if x in features]
    if len(selected_features) < 1:
        selected_features = features

    # In this bit we prepare an empty list to start adding the radar data, as well as making sure all numeric features
    # are scaled for the user to have a pleasant visual experience. As this is the compare tab, we do not care too much
    # for specific values, thus the conversion in the 0-1 domain.

    radar_data = []
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    numerics = df.select_dtypes(include=numerics).columns
    df[numerics] = (df[numerics]-df[numerics].min())/(df[numerics].max()-df[numerics].min())


    # for each player, we check if such a player exists. We then take the first occurence and append their data to the
    # radar plot data
    for player in players:
        players_data = df[df['player'] == player]
        if players_data.shape[0] < 1:
            break
        player_data = players_data.iloc[0]


        radar_data.append(
            go.Scatterpolar(
                r=player_data[selected_features],
                theta=selected_features,
                fill='toself',
                name=player
            )
        )

    # straight forward definition of the layout. As we scaled the data, we can set the range from 0-1
    layout = go.Layout(
        title=f'Radar chart of selected players',
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True
    )

    # returning a full composition of the figure. As plotly is quite robust, non numerical columns that slip through
    # are seemingly ignored.
    return go.Figure(data=radar_data, layout=layout).update_layout(legend=dict(font=dict(family='Arial')), polar=dict(
        radialaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=False, ticks=''),
        angularaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True, ticks='')))


# The next callback follows a lot of similar logic. We check for existing variables and filter for numerical columns
# We give the barchart some names and add the players one for one to the graph to get the correct grouping
@callback(
    Output('compare-players-chart', 'figure'),
    Input('compare-stats-dropdown', 'value'),
    Input('compare-feature-dropdown', 'value'),
    Input('selected-players', 'value'))
def update_compare_feature_dropdown_and_chart(selected_stat, selected_features, players):
    if selected_stat is None:
        return go.Figure(), []

    if players is None:
        return go.Figure(), []

    if len(players) < 1:
        return go.Figure(), []

    df = dataframes[selected_stat].copy()
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    features = list(df.select_dtypes(include=numerics).columns)

    if selected_features is None:
        selected_features = features
    else:
        selected_features = [x for x in selected_features if x in features]
        if len(selected_features) < 1:
            selected_features = features




    # Create the bar chart using Plotly Graph Objects
    bar_data = df[df['player'].isin(players)].sort_values(by='player', ascending=False)
    bar_data = bar_data[selected_features]

    fig = go.Figure()
    for i, player in enumerate(players):
        fig.add_trace(
            go.Bar(
                x=selected_features,
                y=bar_data.iloc[i],
                name=player
            )
        )
    # updating the layout title
    fig.update_layout(title=f'Players performance in the selected features within {selected_stat}', xaxis_title='Player',
                      yaxis_title=None)
    # updating the layout with legend, as well as returning the resulting figure
    return fig.update_layout(legend=dict(font=dict(family='Arial')),
                             xaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1,
                                        showticklabels=True, ticks=''),
                             yaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1,
                                        showticklabels=True, ticks=''))



# This callback updates the features dropdown, with some check for when no stat is selected. It excludes some features.
@callback(
    Output('compare-feature-dropdown', 'options'),
    Output('compare-feature-dropdown', 'value'),
    Input('compare-stats-dropdown', 'value'))
def update_compare_stat_and_feature_dropdown(selected_stat):
    if selected_stat is None:
        selected_stat = 'player_defense'

    df = dataframes[selected_stat].copy()
    features = df.columns.difference([*exclude_columns, 'team', 'club'])
    feature_options = [{'label': feature, 'value': feature} for feature in features]

    return feature_options, features