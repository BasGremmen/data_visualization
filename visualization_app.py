from viz_app.main import app
from viz_app.config import player_tables
from viz_app.data import get_player_data
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go

import plotly.express as px
from dash import html, dcc

data_path = "C:\\Users\\bgrem\\Documents\\Data visualization\\JM0250 Data (2022-2023)\\JM0250 Data (2022-2023)\\Data\\"

# Load your CSV files
shooting_stats = pd.read_csv("{}Fifa World Cup 2022 Player Data\\player_shooting.csv".format(data_path))
defending_stats = pd.read_csv("{}Fifa World Cup 2022 Player Data\\player_defense.csv".format(data_path))

# Create a dictionary for easier DataFrame access
dataframes = {table: get_player_data(table) for table in player_tables}

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

# Columns to exclude from radar chart
exclude_columns = {'age', 'position', 'birth_year'}

if __name__ == '__main__':
    app.layout = html.Div(
        id="app-container",
        children= [
            html.Div([
                html.H1('Soccer Scout Dashboard', style={'textAlign': 'center'}),
            ]),

            dcc.Tabs([
                dcc.Tab(label='Find Players', children=[
                    html.Div([
                        html.Div([
                            html.Label('Select Stat Category'),
                            dcc.Dropdown(
                                id='stats-dropdown',
                                options=[{'label': stat, 'value': stat} for stat in dataframes.keys()],
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
                        html.Div([
                            dcc.Graph(id='scatter-plot'),
                        ], className='twelve columns', style={'marginBottom': '20px'}),
                    ], className='row'),
                ]),

                dcc.Tab(label='Explore Players', children=[
                    html.Div([
                        html.Div([
                            html.Label('Select Stat Category'),
                            dcc.Dropdown(
                                id='explore-stats-dropdown',
                                options=[{'label': stat, 'value': stat} for stat in dataframes.keys()],
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
                    ], className='row', style={'marginBottom': '10px'}),
            ]),
        ])
    ])


    @app.callback(
        Output('feature-dropdown', 'options'),
        Output('team-dropdown', 'options'),
        Input('stats-dropdown', 'value'))
    def update_feature_and_team_dropdown(selected_stat):
        if selected_stat is None:
            return [], []

        df = dataframes[selected_stat]
        teams = df['team'].unique()
        team_options = [{'label': team, 'value': team} for team in teams]

        features = df.columns.difference(['player', 'team']).difference(exclude_columns)
        feature_options = [{'label': feature, 'value': feature} for feature in features]

        return feature_options, team_options


    @app.callback(
        Output('player-dropdown', 'options'),
        Input('team-dropdown', 'value'),
        State('stats-dropdown', 'value'))
    def update_player_dropdown(selected_teams, selected_stat):
        if selected_teams is None or not selected_teams or selected_stat is None:
            return []

        df = dataframes[selected_stat]
        players = df[df['team'].isin(selected_teams)]['player'].unique()
        return [{'label': player, 'value': player} for player in players]


    @app.callback(
        Output('bar-chart', 'figure'),
        Input('stats-dropdown', 'value'),
        Input('feature-dropdown', 'value'),
        Input('player-dropdown', 'value'))
    def update_bar_chart(selected_stat, selected_features, selected_players):
        if selected_stat is None or selected_features is None or not selected_features or selected_players is None or not selected_players:
            return go.Figure()

        df = dataframes[selected_stat]
        bar_data = df[df['player'].isin(selected_players)]

        # Bar colors
        bar_colors = px.colors.qualitative.Plotly[:len(selected_players)]

        return px.bar(bar_data, x='player', y=selected_features, barmode='group', title='Selected Features for Players',
                      color_discrete_sequence=bar_colors)


    @app.callback(
        Output('radar-chart', 'figure'),
        Input('stats-dropdown', 'value'),
        Input('feature-dropdown', 'value'),
        Input('player-dropdown', 'value'))
    def update_radar_chart(selected_stat, selected_features, selected_players):
        radar_colors = px.colors.qualitative.Plotly[:len(selected_players)]
        if selected_stat is None or selected_features is None or not selected_features or selected_players is None or not selected_players:
            return go.Figure()

        df = dataframes[selected_stat]
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


    @app.callback(
        Output('scatter-plot', 'figure'),
        Input('stats-dropdown', 'value'),
        Input('feature-dropdown', 'value'),
        Input('player-dropdown', 'value'))
    def update_scatter_plot(selected_stat, selected_features, selected_players):
        if selected_stat is None or selected_features is None or not selected_features or len(
                selected_features) < 2 or selected_players is None or not selected_players:
            return go.Figure()

        df = dataframes[selected_stat]
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


    @app.callback(
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


    @app.callback(
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


    app.run_server(debug=False, dev_tools_ui=False)
