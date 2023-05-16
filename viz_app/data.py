import pandas as pd
from viz_app.config import data_path


# here we retrieve data from the player tables using the data format of the data provided.
def get_player_data(table):

    player_data_path = "{}Fifa World Cup 2022 Player Data\\{}.csv".format(data_path, table)
    df = pd.read_csv(player_data_path)

    return df


# similar function but for team datasets, not used
def get_team_data(table):
    team_data_path = "{}Fifa World Cup 2022 Team Data\\{}.csv".format(data_path, table)
    df = pd.read_csv(team_data_path)

    return df
