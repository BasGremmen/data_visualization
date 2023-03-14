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
                    dcc.Graph(id="graph")
                ],
            ),
        ],
    )

    @app.callback(
        Output('feature-select', 'options'),
        Input('data-select', 'value'),
    )
    def update_feature_options(table):
        options = get_player_data(table).columns
        return [{'label': i, 'value': i} for i in options if i not in ['team', 'player']]

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


    app.run_server(debug=False, dev_tools_ui=False)