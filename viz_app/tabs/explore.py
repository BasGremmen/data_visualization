from dash import callback, Input, Output, dcc, html, Dash, State
from ..config import player_tables

layout = html.Div([
    html.Div([
        html.Label('Select Stat Category'),
        dcc.Dropdown(
            id='explore-stats-dropdown',
            options=[{'label': stat, 'value': stat} for stat in player_tables],
            style={'width': '100%'}
        ),
    ], className='six columns'),

    html.Div([
        html.Label('Select Feature'),
        dcc.Dropdown(
            id='explore-feature-dropdown',
            style={'width': '100%'}
        ),
    ], className='six columns'),

    html.Div([
        dcc.Graph(id='top-players-chart', clickData=None),
    ], className='twelve columns', style={'marginBottom': '20px'}),
    html.Div([
        dcc.Graph(id='explore-radar-chart'),
    ], className='twelve columns', style={'marginBottom': '20px'}),
], className='row', style={'marginBottom': '10px'})


@callback(
    Output('explore-radar-chart', 'figure'),
    Input('top-players-chart', 'clickData'),
    State('explore-stats-dropdown', 'value'),
    State('explore-feature-dropdown', 'value'))


def update_explore_radar_chart(clickData, selected_stat, selected_feature):
    if clickData is None or selected_stat is None:
        return go.Figure()

    selected_players = [point['customdata'][0] for point in clickData['points']]

    df = dataframes[selected_stat]
    radar_data = []

    for player in selected_players:
        player_data = df[df['player'] == player].iloc[0]
        features = df.columns.difference(['player', 'team']).difference(exclude_columns)
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
