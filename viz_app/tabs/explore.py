# standard dash imports, plotly imports, pandas, as well as some custom functions and variables

from dash import callback, Input, Output, dcc, html, Dash, State
import plotly.graph_objs as go
import plotly.express as px

from viz_app.main import dataframes, exclude_columns
from viz_app.config import player_tables
import pandas as pd

# Here we define the tab. It consists of a few rows, of which the first 2 contain the input elements.
layout = dcc.Tab(label='Explore Players', children=[
    html.Div([
        html.Div([
            html.Label('Select Stat Category'),
            dcc.Dropdown(
                id='explore-stats-dropdown',
                options=[{'label': stat, 'value': stat} for stat in player_tables],
                style={'width': '100%'},
                value='player_defense'
            ),
        ], className='six columns'),

        html.Div([
            html.Label('Select Feature'),
            dcc.Dropdown(
                id='explore-feature-dropdown',
                style={'width': '100%'},
                value='age'
            ),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '10px'}),

    html.Div([
        html.Div([
            html.Label('Filter by Age'),
            dcc.RangeSlider(
                id='age-range-slider',
                min=15,
                max=40,
                value=[15, 40],
                marks={i: f'{i}' for i in range(15, 41, 5)}
            ),
        ], className='six columns'),

        html.Div([
            html.Label('Filter by Position'),
            dcc.Dropdown(
                id='position-dropdown',
                options=[{'label': pos, 'value': pos} for pos in ['GK', 'DF', 'MF', 'FW']],
                multi=True,
                style={'width': '100%'}
            ),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '10px'}),

    # The output row, which contains the bar chart with top players as well as the hover data radar chart
    html.Div([
        html.Div([
            dcc.Graph(id='top-players-chart', clickData=None),
        ], className='six columns'),
        html.Div([
            dcc.Graph(id='explore-radar-chart'),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '10px'}),

])

# This is a simple callback which reads the click data of the bar chart and updates the app wide player selection
@callback(
    Output('selected-players', 'value'),
    Input('top-players-chart', 'clickData'),
    State('selected-players', 'value'),

)
def add_to_selection(clickData, players):
    if players is None:
        players = []

    if clickData is None:
        return players

    player = clickData['points'][0]['customdata'][0]
    if player not in players:
        players.append(player)
    return players

# The radar plot update based on hover
@callback(
    Output('explore-radar-chart', 'figure'),
    Input('top-players-chart', 'hoverData'),
    State('explore-stats-dropdown', 'value'))
def update_explore_radar_chart(hoverData, selected_stat):
    # Initiate a title if no hover data is found and return empty figure
    title = 'Hover over a player to view'
    if hoverData is None or selected_stat is None:
        layout_empty = go.Layout(title=title)
        return go.Figure(layout=layout_empty)

    # retrieve the player
    selected_players = [point['customdata'][0] for point in hoverData['points']]


    # copy clean frame
    df = dataframes[selected_stat].copy()
    radar_data = []

    # cycle through players and add their data to the radar plot. The code assumes multiple players but in practice
    # only 1 player is hovered and processed
    for player in selected_players:
        player_data = df[df['player'] == player].iloc[0]
        features = df.columns.difference([*exclude_columns, 'club', 'position', 'age', 'player', 'team'])
        radar_data.append(
            go.Scatterpolar(
                r=player_data[features],
                theta=features,
                fill='toself',
                name=player
            )
        )
        title = f'Radar plot with features of {player}'

    # setting the layout. Note the double use of max().max() to get the maximum of the dataset to scale the radar plot
    # to. It is somewhat problematic, as it scales features to the maximum of all variables. A workaround is possible
    # but not without a proper refactor to guarantee the speed and optimization of the app
    layout = go.Layout(
        title=title,
        polar=dict(radialaxis=dict(visible=True, range=[0, max(df[features].max().max(), 1)])),
        showlegend=True
    )

    # here we return the figure
    return go.Figure(data=radar_data, layout=layout).update_layout(legend=dict(font=dict(family='Arial')), polar=dict(
        radialaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=False, ticks=''),
        angularaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True, ticks='')))

# this is a big callback which updates both the feature dropdown as well as the bar chart containing top players within
# the feature selected
@callback(
    Output('top-players-chart', 'figure'),
    Output('explore-feature-dropdown', 'options'),
    Input('explore-stats-dropdown', 'value'),
    Input('explore-feature-dropdown', 'value'),
    Input('age-range-slider', 'value'),
    Input('position-dropdown', 'value'))
def update_explore_dropdown_and_chart(selected_stat, selected_feature, age_range, positions):
    # check for selected dataset
    if selected_stat is None:
        return go.Figure(), []

    # getting a clean dataframe copy, as well as cleaning up some of the columns and sanitizing age dynamically.
    # Ideally this would be moved in the application start up in a refactor.
    df = dataframes[selected_stat].copy()
    df['age'] = df['age'].apply(lambda x: x[:2])
    df['age'] = pd.to_numeric(df['age'])
    features = df.columns.difference([*exclude_columns, 'team', 'club'])
    feature_options = [{'label': feature, 'value': feature} for feature in features]

    # If no feature is selected that is valid, we return the first feature
    if selected_feature not in features:
        selected_feature = features[0]

    # if age_range is set, we filter by age
    if age_range is not None:
        # Filter by age
        df = df[(df['age'] >= age_range[0]) & (df['age'] <= age_range[1])]

    # if positions is set, we filter by position
    if positions is not None:
        # Filter by position
        if positions:
            df = df[df['position'].isin(positions)]

    # Selecting the top players in the stat
    top_players = df.nlargest(10, selected_feature).sort_values(by=selected_feature, ascending=False)

    # Generating some colors, we only need 10 as we only select the top 10 players
    bar_colors = px.colors.qualitative.Plotly[:10]

    # instantiate empty figure
    fig = go.Figure()

    # adding the player_data in one go
    fig.add_trace(
        go.Bar(
            x=top_players['player'],
            y=top_players[selected_feature],
            customdata=top_players[['player']].values,
            marker_color=bar_colors
        )
    )

    # updating the layout title
    fig.update_layout(title=f'Top 10 Players in {selected_feature}', xaxis_title='Player',
                      yaxis_title=selected_feature)

    # adding some figure layouting and returning the options for the features as well (feature_options)
    return fig.update_layout(legend=dict(font=dict(family='Arial')),
                             xaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1,
                                        showticklabels=True, ticks=''),
                             yaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1,
                                        showticklabels=True, ticks='')), feature_options
