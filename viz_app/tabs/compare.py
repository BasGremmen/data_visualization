from dash import callback, Input, Output, dcc, html, Dash, State
import plotly.graph_objs as go
import plotly.express as px

from viz_app.main import dataframes, exclude_columns
from viz_app.config import player_tables
import pandas as pd

layout = dcc.Tab(label='Compare Players', children=[
    html.Div([
        html.Div([
            html.Label('Select Stat Category'),
            dcc.Dropdown(
                id='compare-stats-dropdown',
                options=[{'label': stat, 'value': stat} for stat in player_tables],
                style={'width': '100%'}
            ),
        ], className='six columns'),

        html.Div([
            html.Label('Select Feature'),
            dcc.Dropdown(
                id='compare-feature-dropdown',
                style={'width': '100%'}
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

@callback(
    Output('compare-radar-chart', 'figure'),
    State('selected-players', 'value'),
    Input('compare-stats-dropdown', 'value'))
def update_compare_radar_chart(players, selected_stat):
    if selected_stat is None:
        return go.Figure(), []

    df = dataframes[selected_stat].copy()
    df['age'] = df['age'].apply(lambda x: x[:2])
    df['age'] = pd.to_numeric(df['age'])
    features = df.columns.difference([*exclude_columns, 'team', 'club'])
    radar_data = []

    for player in players:
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

    layout = go.Layout(
        title=f'Radar chart of selected players',
        polar=dict(radialaxis=dict(visible=True, range=[0, max(df[features].max().max(), 1)])),
        showlegend=True
    )

    return go.Figure(data=radar_data, layout=layout).update_layout(legend=dict(font=dict(family='Arial')), polar=dict(
        radialaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=False, ticks=''),
        angularaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True, ticks='')))
