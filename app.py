import pandas as pd

from viz_app.main import app
from viz_app.views.menu import make_menu_layout
from viz_app.views.scatterplot import Scatterplot
from viz_app.data import get_player_data

from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output


theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}


if __name__ == '__main__':
    # Create data
    df = get_player_data('player_defense')

    app.layout = html.Div(
        id="app-container",
        children=[
            # Left column
            html.Div(
                id="left-column",
                className="three columns",
                children=make_menu_layout()
            ),

            # Right column
            html.Div(
                id="right-column",
                className="nine columns",
                children=[
                    dcc.Graph(id="graph"),
                    dcc.Graph(id="player-details"),
                ],
            ),
        ],
    )

    @app.callback(
        Output('feature-select', 'options'),
        Input('data-select', 'value'),
    )
    def update_feature_options(table):
        df = get_player_data(table)
        cols = [col for col in df if df[col].dtypes == "float64"]
        return [{'label': i, 'value': i} for i in cols if i not in ['team', 'player']]

    @app.callback(
        Output('feature-select', 'value'),
        Input('feature-select', 'options')
    )
    def update_feature_selected(options):
        return options[0]['value']


    @app.callback(
        Output('graph', "figure"),
        Input("data-select", "value"),
        Input("feature-select", "value"),
        Input("team-select", "value"),
        )
    def update_bar_chart(table, feature, team):
        df = get_player_data(table)
        fig = px.bar(df[df['team'] == team], x='player', y=feature)
        return fig


    @app.callback(
        Output('player-details', 'figure'),
        Input("graph", "clickData"),
        Input("data-select", "value"),
        Input("team-select", "value")
    )
    def update_player_details(data, table, team):
        df = get_player_data(table)
        if data:
            player = data['points'][0]['label']
        else:
            player = df[df['team'] == team].iloc[0]['player']

        cols = [col for col in df if df[col].dtypes == "float64"]

        player_input = pd.DataFrame(dict(
            r=list(df[df['player'] == player][cols].iloc[0]),
            theta=cols))

        fig = px.line_polar(player_input, r='r', theta='theta', line_close=True)
        return fig


    app.run_server(debug=False, dev_tools_ui=False)