from dash import Dash
from viz_app.data import get_player_data
from viz_app.config import player_tables


app = Dash(__name__, external_stylesheets=["https://use.fontawesome.com/releases/v5.7.2/css/all.css"])

# Create a dictionary for easier DataFrame access
dataframes = {table: get_player_data(table) for table in player_tables}

# Columns to exclude from radar chart
exclude_columns = {'birth_year'}

app.title = "Football Visualization"
