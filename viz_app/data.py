import pandas as pd


def get_data():

    player_data_path = "C:\\Users\\bgrem\\Documents\\Repositories\\data_visualization\\data\\Fifa World Cup 2022 Player Data\\player_defense.csv"
    df = pd.read_csv(player_data_path)

    return df
