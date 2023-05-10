from dash import callback, Input, Output, dcc, html, Dash, State
import plotly.graph_objs as go
import plotly.express as px

from viz_app.main import dataframes, exclude_columns
from viz_app.config import player_tables

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
        ], className='six columns', style={'marginBottom': '20px'}),

        html.Div([
            dcc.Graph(id='radar-chart'),
        ], className='six columns', style={'marginBottom': '20px'}),
    ], className='row'),

    html.Div([
        dcc.Graph(id='scatter-plot'),

    ], className='row', style={"marginBottom": '20px'}),
])


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

    features = df.columns.difference(['player', 'team']).difference(exclude_columns)
    feature_options = [{'label': feature, 'value': feature} for feature in features]

    return feature_options, team_options


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


@callback(
    Output('bar-chart', 'figure'),
    Input('stats-dropdown', 'value'),
    Input('feature-dropdown', 'value'),
    Input('player-dropdown', 'value'))
def update_bar_chart(selected_stat, selected_features, selected_players):
    if selected_stat is None or selected_features is None or not selected_features or selected_players is None or not selected_players:
        return go.Figure()

    df = dataframes[selected_stat].copy()
    bar_data = df[df['player'].isin(selected_players)]

    # Bar colors
    bar_colors = px.colors.qualitative.Plotly[:len(selected_players)]

    return px.bar(bar_data, x='player', y=selected_features, barmode='group', title='Selected Features for Players',
                  color_discrete_sequence=bar_colors)


@callback(
    Output('radar-chart', 'figure'),
    Input('stats-dropdown', 'value'),
    Input('feature-dropdown', 'value'),
    Input('player-dropdown', 'value'))
def update_radar_chart(selected_stat, selected_features, selected_players):
    if selected_stat is None or selected_features is None or not selected_features or selected_players is None or not selected_players:
        return go.Figure()

    df = dataframes[selected_stat].copy()
    radar_data = []

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

    layout = go.Layout(
        title=f'Radar chart of selected players',
        polar=dict(radialaxis=dict(visible=True, range=[0, max(df[selected_features].max().max(), 1)])),
        showlegend=True
    )

    return go.Figure(data=radar_data, layout=layout).update_layout(legend=dict(font=dict(family='Arial')), polar=dict(
        radialaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=False, ticks=''),
        angularaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True, ticks='')))


@callback(
    Output('scatter-plot', 'figure'),
    Input('stats-dropdown', 'value'),
    Input('feature-dropdown', 'value'),
    Input('player-dropdown', 'value'))
def update_scatter_plot(selected_stat, selected_features, selected_players):
    if selected_stat is None or selected_features is None or not selected_features or len(
            selected_features) < 2 or selected_players is None or not selected_players:
        return go.Figure()

    df = dataframes[selected_stat].copy()
    selected_data = df[df['player'].isin(selected_players)]

    fig = go.Figure()

    for player in selected_players:
        player_data = selected_data[selected_data['player'] == player]
        fig.add_trace(
            go.Scatter(x=player_data[selected_features[0]], y=player_data[selected_features[1]], mode='markers',
                       marker=dict(size=12), name=player, text=player_data['team'],
                       hovertemplate='%{text}<br>%{xaxis.title.text}: %{x}<br>%{yaxis.title.text}: %{y}'))

    fig.update_layout(title=f'Scatter plot of {selected_features[0]} vs {selected_features[1]}',
                      xaxis_title=selected_features[0], yaxis_title=selected_features[1])

    return fig.update_layout(legend=dict(font=dict(family='Arial')),
                             xaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True,
                                        ticks=''),
                             yaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True,
                                        ticks=''))
