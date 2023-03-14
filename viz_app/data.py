import pandas as pd


def get_player_data(table):

    player_data_path = "C:\\Users\\bgrem\\Documents\\Repositories\\data_visualization\\data\\Fifa World Cup 2022 Player Data\\{}.csv".format(table)
    df = pd.read_csv(player_data_path)

    return df


def get_team_data(table):
    team_data_path = "C:\\Users\\bgrem\\Documents\\Repositories\\data_visualization\\data\\Fifa World Cup 2022 Team Data\\{}.csv".format(table)
    df = pd.read_csv(team_data_path)

    return df
