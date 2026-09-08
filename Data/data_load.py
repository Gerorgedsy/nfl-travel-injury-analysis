import nflreadpy as nfl
import pandas as pd

"""
Pulls data from nflreadpy and saves it all directly into CSV files in the Data directory.
To access stadium information, please download the CSV directly from the following link:
    https://github.com/greerreNFL/Stadiums/blob/main/data/stadiums.csv
"""

def load_data(schedules=True, injuries=True, snap_counts=True, players=True, pbp=False):
    """
    This function loads NFL data using the nflreadpy library, and saves the data to CSV files in the Data directory.
    
    Arguments:
    schedules : bool, optional
        If True, load and save the NFL schedules data. Default is True.
    injuries : bool, optional
        If True, load and save the NFL injuries data. Default is True.
    snap_counts : bool, optional
        If True, load and save the NFL snap counts data. Default is True.
    players : bool, optional
        If True, load and save the NFL players data. Default is True.
    pbp : bool, optional
        If True, load and save the NFL play-by-play data. Default is False.
    """

    arguments = locals()

    for param_name, param_value in arguments.items():
        if param_value:
            if param_name == "schedules":
                schedules = nfl.load_schedules(seasons=True).to_pandas()
                schedules.to_csv("Data/schedules.csv", index=False)
                print("Schedules data loaded and saved to Data/schedules.csv")
            if param_name == "injuries":
                injuries = nfl.load_injuries(seasons=True).to_pandas()
                injuries.to_csv("Data/injuries.csv", index=False)
                print("Injuries data loaded and saved to Data/injuries.csv")
            if param_name == "snap_counts":
                snap_counts = nfl.load_snap_counts(seasons=True).to_pandas()
                snap_counts.to_csv("Data/snap_counts.csv", index=False)
                print("Snap counts data loaded and saved to Data/snap_counts.csv")
            if param_name == "players":
                players = nfl.load_players().to_pandas()
                players.to_csv("Data/players.csv", index=False)
                print("Players data loaded and saved to Data/players.csv")
            if param_name == "pbp":
                pbp = nfl.load_pbp(seasons=True).to_pandas()
                pbp.to_csv("Data/pbp.csv", index=False)
                print("Play-by-play data loaded and saved to Data/pbp.csv")

    print("Data loading complete")

if __name__ == "__main__":
    load_data()