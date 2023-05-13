from dash import callback, Input, Output, dcc, html, Dash, State
import plotly.graph_objs as go
import plotly.express as px

from viz_app.main import dataframes, exclude_columns
from viz_app.config import player_tables
import pandas as pd

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

    html.Div([
        html.Div([
            dcc.Graph(id='top-players-chart', clickData=None),
        ], className='six columns'),
        html.Div([
            dcc.Graph(id='explore-radar-chart'),
        ], className='six columns'),
    ], className='row', style={'marginBottom': '10px'}),

])


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


@callback(
    Output('explore-radar-chart', 'figure'),
    Input('top-players-chart', 'hoverData'),
    State('explore-stats-dropdown', 'value'))
def update_explore_radar_chart(hoverData, selected_stat):
    if hoverData is None or selected_stat is None:
        return go.Figure()

    selected_players = [point['customdata'][0] for point in hoverData['points']]

    df = dataframes[selected_stat].copy()
    radar_data = []

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

    layout = go.Layout(
        title=f'Radar chart of selected players',
        polar=dict(radialaxis=dict(visible=True, range=[0, max(df[features].max().max(), 1)])),
        showlegend=True
    )

    return go.Figure(data=radar_data, layout=layout).update_layout(legend=dict(font=dict(family='Arial')), polar=dict(
        radialaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=False, ticks=''),
        angularaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True, ticks='')))

@callback(
    Output('top-players-chart', 'figure'),
    Output('explore-feature-dropdown', 'options'),
    Input('explore-stats-dropdown', 'value'),
    Input('explore-feature-dropdown', 'value'),
    Input('age-range-slider', 'value'),
    Input('position-dropdown', 'value'))
def update_explore_dropdown_and_chart(selected_stat, selected_feature, age_range, positions):
    if selected_stat is None:
        return go.Figure(), []

    df = dataframes[selected_stat].copy()
    df['age'] = df['age'].apply(lambda x: x[:2])
    df['age'] = pd.to_numeric(df['age'])
    features = df.columns.difference([*exclude_columns, 'team', 'club'])
    feature_options = [{'label': feature, 'value': feature} for feature in features]

    # Update the selected feature when the dataset changes
    if selected_feature not in features:
        selected_feature = features[0]

    if age_range is not None:
        # Filter by age
        df = df[(df['age'] >= age_range[0]) & (df['age'] <= age_range[1])]

    if positions is not None:
        # Filter by position
        if positions:
            df = df[df['position'].isin(positions)]

    # Create the bar chart using Plotly Graph Objects
    top_players = df.nlargest(10, selected_feature).sort_values(by=selected_feature, ascending=False)

    # Bar colors
    bar_colors = px.colors.qualitative.Plotly[:10]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=top_players['player'],
            y=top_players[selected_feature],
            customdata=top_players[['player']].values,
            marker_color=bar_colors
        )
    )

    fig.update_layout(title=f'Top 10 Players in {selected_feature}', xaxis_title='Player',
                      yaxis_title=selected_feature)

    return fig.update_layout(legend=dict(font=dict(family='Arial')),
                             xaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1,
                                        showticklabels=True, ticks=''),
                             yaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1,
                                        showticklabels=True, ticks='')), feature_options
