from viz_app.main import app
from viz_app.views.menu import make_menu_layout
from viz_app.views.scatterplot import Scatterplot
from viz_app.data import get_data

from dash import html
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
    df = get_data()

    # Instantiate custom views
    scatterplot1 = Scatterplot("Tackles vs Tackles won", 'tackles', 'tackles_won', df)

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
                    scatterplot1
                ],
            ),
        ],
    )

    # Define interactions
    @app.callback(
        Output(scatterplot1.html_id, "figure"),
        Input("select-color-scatter-1", "value")
    )
    def update_scatter_1(selected_color):
        return scatterplot1.update(selected_color)


    app.run_server(debug=False, dev_tools_ui=False)