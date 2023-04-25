from dash import dcc, html
from viz_app.data import get_player_data, get_team_data
from ..config import player_tables

def generate_wrapper():
    plus_icon = html.I(className="fa fa-plus", style=dict(display="inline-block"))
    return html.Div(
        id="right-column",
        className="nine columns",
        children=[
            html.Div(id="graph-block",
                     className="row",
                     style={"background": "white"},
                     children=[html.Label("Select feature for bar chart"),
                               dcc.Dropdown(
                                   id="feature-select",
                                   className="three columns",
                                   options=[{"label": i, "value": i} for i in
                                            get_player_data('player_defense').columns[1:]],
                                   value=get_player_data('player_defense').columns[1],
                               ),
                               dcc.Graph(id="graph", className="nine columns")
                               ]),
            html.Br(),
            html.Div(
                id="player-block",
                style={"background": "white"},
                className="row",
                children=[
                    html.H1(id="player-name", style={"textAlign": "center"}),
                    dcc.Graph(id="player-details"),
                    html.Button(children=[plus_icon], style={"float": "right"})
                ]
            )
        ],
    )

