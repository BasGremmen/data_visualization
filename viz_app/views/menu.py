from dash import dcc, html
from viz_app.data import get_player_data, get_team_data
from ..config import player_tables

def generate_description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Football Visualization"),
            html.Div(
                id="intro",
                children="The player data can be analysed here",
            ),
        ],
    )


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Label("Select data"),
            dcc.Dropdown(
                id="data-select",
                options=[{"label": i, "value": i} for i in player_tables],
                value=player_tables[0]
            ),
            html.Label("Filter players by team"),
            dcc.Dropdown(
                id="team-select",
                options=[{"label": i, "value": i} for i in get_team_data('team_data')['team']],
                value=get_team_data('team_data')['team'][0]
            ),

        ], style={"textAlign": "float-left"}
    )


def make_menu_layout():
    return [generate_description_card(), generate_control_card()]
