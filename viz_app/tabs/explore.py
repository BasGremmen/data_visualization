from dash import callback, Input, Output, dcc, html, Dash, State
import plotly.graph_objs as go
import plotly.express as px

from viz_app.main import dataframes, exclude_columns
from viz_app.config import player_tables

layout = dcc.Tab(label='Explore Players', children=[
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


@callback(
    Output('top-players-chart', 'figure'),
    Output('explore-feature-dropdown', 'options'),
    Input('explore-stats-dropdown', 'value'))


def update_explore_dropdown_and_chart(selected_stat):
    if selected_stat is None:
        return go.Figure(), []

    df = dataframes[selected_stat]
    features = df.columns.difference(['player', 'team']).difference(exclude_columns)
    feature_options = [{'label': feature, 'value': feature} for feature in features]

    # Create the bar chart using Plotly Graph Objects
    top_players = df.nlargest(10, features[0])

    # Bar colors
    bar_colors = px.colors.qualitative.Plotly[:10]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=top_players['player'],
            y=top_players[features[0]],
            customdata=top_players[['player']].values,
            marker_color=bar_colors
        )
    )

    fig.update_layout(title=f'Top 10 Players in {features[0]}', xaxis_title='Player', yaxis_title=features[0])

    return fig.update_layout(legend=dict(font=dict(family='Arial')),
                             xaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True,
                                        ticks=''),
                             yaxis=dict(linecolor='darkgray', gridcolor='lightgray', linewidth=1, showticklabels=True,
                                        ticks='')), feature_options
