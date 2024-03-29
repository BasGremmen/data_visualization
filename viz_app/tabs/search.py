# Similar imports as in explore and compare
from dash import callback, Input, Output, dcc, html, Dash, State
import plotly.graph_objs as go
import plotly.express as px

from viz_app.main import dataframes, exclude_columns
from viz_app.config import player_tables

# The html structure is almost identical to the explore tab, with 2 rows of input and 1 row of output
layout = dcc.Tab(label='Find Players', children=[
    html.Div([
        html.Div([
            html.Label('Select Stat Category'),
            dcc.Dropdown(
                id='stats-dropdown',
                options=[{'label': stat, 'value': stat} for stat in player_tables],
                style={'width': '100%'}
            ),
        ], className='six columns'),

        html.Div([
            html.Label('Select Features'),
            dcc.Dropdown(
                id='feature-dropdown',
                multi=True,
                style={'width': '100%'}
            ),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '10px'}),

    html.Div([
        html.Div([
            html.Label('Select Teams'),
            dcc.Dropdown(
                id='team-dropdown',
                multi=True,
                placeholder='Select teams',
                style={'width': '100%'}
            ),
        ], className='six columns'),

        html.Div([
            html.Label('Select Players'),
            dcc.Dropdown(
                id='player-dropdown',
                multi=True,
                style={'width': '100%'}
            ),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '10px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='bar-chart'),
        ], className='six columns'),

        html.Div([
            dcc.Graph(id='radar-chart'),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '20px'}),
])


# Here we update the feature-dropdown and team-dropdown to only contain numerical columns
@callback(
    Output('feature-dropdown', 'options'),
    Output('team-dropdown', 'options'),
    Input('stats-dropdown', 'value'))
def update_feature_and_team_dropdown(selected_stat):
    if selected_stat is None:
        return [], []

    df = dataframes[selected_stat].copy()
    teams = df['team'].unique()
    team_options = [{'label': team, 'value': team} for team in teams]
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    features = df.select_dtypes(include=numerics).columns.difference(['player', 'team']).difference(exclude_columns)
    feature_options = [{'label': feature, 'value': feature} for feature in features]

    return feature_options, team_options


# This callback simply update the player dropdown with the selected team and dataset dropdown.
@callback(
    Output('player-dropdown', 'options'),
    Input('team-dropdown', 'value'),
    State('stats-dropdown', 'value'))
def update_player_dropdown(selected_teams, selected_stat):
    if selected_teams is None or not selected_teams or selected_stat is None:
        return []

    df = dataframes[selected_stat].copy()
    players = df[df['team'].isin(selected_teams)]['player'].unique()
    return [{'label': player, 'value': player} for player in players]


# Here we update the bar chart based on the input menus
@callback(
    Output('bar-chart', 'figure'),
    Input('stats-dropdown', 'value'),
    Input('feature-dropdown', 'value'),
    Input('player-dropdown', 'value'))
def update_bar_chart(selected_stat, selected_features, selected_players):
    # some checks for valid data
    if selected_stat is None:
        return go.Figure()

    bar_data = dataframes[selected_stat].copy()

    if selected_players is None or len(selected_players) < 1:
        selected_players = list(bar_data['player'])

    bar_data = bar_data[bar_data['player'].isin(selected_players)]

    if selected_features is None or len(selected_features) < 1:
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        selected_features = bar_data.select_dtypes(include=numerics).columns.difference(['player', 'team']).difference(exclude_columns)

    # Bar colors based on amount of data
    bar_colors = px.colors.qualitative.Plotly[:bar_data.shape[1]]

    # simply returning the data
    return px.bar(bar_data, x='player', y=selected_features, custom_data=['player'], barmode='group', title='Selected Features for Players',
                  color_discrete_sequence=bar_colors)

# The radar chart updates based on selected players
@callback(
    Output('radar-chart', 'figure'),
    Input('stats-dropdown', 'value'),
    Input('feature-dropdown', 'value'),
    Input('player-dropdown', 'value'))
def update_radar_chart(selected_stat, selected_features, selected_players):
    # check for valid data
    if selected_stat is None or selected_features is None or not selected_features or selected_players is None or not selected_players:
        return go.Figure()

    df = dataframes[selected_stat].copy()
    radar_data = []

    # for every player, add their data
    for player in selected_players:
        player_data = df[df['player'] == player].iloc[0]
        radar_data.append(
            go.Scatterpolar(
                r=player_data[selected_features],
                theta=selected_features,
                fill='toself',
                name=player
            )
        )
    # update radar chart title and range using the max().max() trick as discussed in the explore,py
    layout = go.Layout(
        title=f'Radar chart of selected players',
        polar=dict(radialaxis=dict(visible=True, range=[0, max(df[selected_features].max().max(), 1)])),
        showlegend=True
    )

    # returning the figure with the updated layout
    return go.Figure(data=radar_data, layout=layout).update_layout(legend=dict(font=dict(family='Arial')), polar=dict(
        radialaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=False, ticks=''),
        angularaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True, ticks='')))


# clicking within the bar graph allows for player selection using this callback
@callback(
    Output('selected-players', 'value', allow_duplicate=True),
    Input('bar-chart', 'clickData'),
    State('selected-players', 'value'),
    prevent_initial_call=True
)
def add_to_selection(clickData, players):
    if players is None:
        players = []

    if clickData is None:
        return players


    player = clickData['points'][0]['label']
    if player not in players:
        players.append(player)
    return players