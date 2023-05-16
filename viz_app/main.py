# in this file, some variables get initiated (Such as the app)
# The datasets are loaded into a dictionary to easily access the different dataframes using a function
# called get_player_data, which uses some of the config.py 's defined variables.

from dash import Dash
from viz_app.data import get_player_data
from viz_app.config import player_tables


# loading the app including the stylesheet included in the provided example app
app = Dash(__name__, external_stylesheets=["https://use.fontawesome.com/releases/v5.7.2/css/all.css"])

# Create a dictionary for easier DataFrame access
dataframes = {table: get_player_data(table) for table in player_tables}

# Columns to exclude from radar chart
exclude_columns = {'birth_year'}

# Title of the window
app.title = "Football Visualization"
