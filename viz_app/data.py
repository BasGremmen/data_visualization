import pandas as pd
import os


def get_player_data(table):
    data_path = os.getenv('DATA_PATH')

    player_data_path = "{}Fifa World Cup 2022 Player Data\\{}.csv".format(data_path, table)
    df = pd.read_csv(player_data_path)

    return df


def get_team_data(table):
    data_path = os.getenv('DATA_PATH')
    team_data_path = "{}Fifa World Cup 2022 Team Data\\{}.csv".format(data_path, table)
    df = pd.read_csv(team_data_path)

    return df
