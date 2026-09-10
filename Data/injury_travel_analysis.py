import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# ============================================================
# NFL Injury, Travel Distance, and Stadium Location Analysis
# Seasons: 2009-2025
# ============================================================

# -----------------------------
# 1. Load data
# -----------------------------

injuries = pd.read_csv(
    "Data/injuries_preprocessed.csv",
    low_memory=False
)

# Keep only the first observation of each injury spell
injuries = injuries[
    injuries["is_new_spell"] == True
].copy()
schedules = pd.read_csv("Data/schedules.csv", low_memory=False)
stadiums = pd.read_csv("Data/stadiums.csv", low_memory=False)

print("=== DATA LOADED ===")
print("Injuries:", injuries.shape)
print("Schedules:", schedules.shape)
print("Stadiums:", stadiums.shape)


# -----------------------------
# 2. Restrict to valid seasons
# -----------------------------

START_SEASON = 2009
END_SEASON = 2025

injuries = injuries[
    (injuries["season"] >= START_SEASON) &
    (injuries["season"] <= END_SEASON) &
    (injuries["game_type"] == "REG")
].copy()

schedules = schedules[
    (schedules["season"] >= START_SEASON) &
    (schedules["season"] <= END_SEASON) &
    (schedules["game_type"] == "REG")
].copy()


# -----------------------------
# 3. Clean key columns
# -----------------------------

injuries = injuries.dropna(
    subset=["season", "week", "team", "gsis_id"]
)

schedules = schedules.dropna(
    subset=["season", "week", "home_team", "away_team", "stadium_id"]
)

injuries["season"] = injuries["season"].astype(int)
injuries["week"] = injuries["week"].astype(int)

schedules["season"] = schedules["season"].astype(int)
schedules["week"] = schedules["week"].astype(int)


# -----------------------------
# 4. Count unique injured players
#    per team-week
# -----------------------------

injury_counts = (
    injuries
    .groupby(["season", "week", "team"])
    .size()
    .reset_index(name="new_injuries")
)

print("\n=== INJURY COUNTS ===")
print(injury_counts.head())
print("Rows:", len(injury_counts))


# -----------------------------
# 5. Convert schedule to
#    one row per team-game
# -----------------------------

home_games = schedules[
    [
        "game_id",
        "season",
        "week",
        "home_team",
        "away_team",
        "stadium_id",
        "stadium",
        "surface",
        "roof"
    ]
].copy()

home_games = home_games.rename(
    columns={
        "home_team": "team",
        "away_team": "opponent"
    }
)

home_games["home_away"] = "home"


away_games = schedules[
    [
        "game_id",
        "season",
        "week",
        "away_team",
        "home_team",
        "stadium_id",
        "stadium",
        "surface",
        "roof"
    ]
].copy()

away_games = away_games.rename(
    columns={
        "away_team": "team",
        "home_team": "opponent"
    }
)

away_games["home_away"] = "away"


team_games = pd.concat(
    [home_games, away_games],
    ignore_index=True
)


# -----------------------------
# 6. Merge stadium coordinates
# -----------------------------

stadium_info = stadiums[
    [
        "stadium_id",
        "stadium_name",
        "lat",
        "lon",
        "city",
        "state",
        "surface_type",
        "roof_type"
    ]
].copy()

team_games = team_games.merge(
    stadium_info,
    on="stadium_id",
    how="left"
)


# -----------------------------
# 7. Merge injury counts
# -----------------------------

analysis = team_games.merge(
    injury_counts,
    on=["season", "week", "team"],
    how="left"
)

analysis["new_injuries"] = (
    analysis["new_injuries"]
    .fillna(0)
    .astype(int)
)


# ============================================================
# PART A: TRAVEL DISTANCE
# ============================================================

# -----------------------------
# 8. Determine each team's
#    home stadium coordinates
# -----------------------------

# Use each team's most common HOME stadium
# over the 2009-2025 sample.

home_stadiums = (
    analysis[analysis["home_away"] == "home"]
    .dropna(subset=["lat", "lon"])
    .groupby("team")
    .agg(
        home_lat=("lat", "median"),
        home_lon=("lon", "median")
    )
    .reset_index()
)

analysis = analysis.merge(
    home_stadiums,
    on="team",
    how="left"
)


# -----------------------------
# 9. Haversine distance function
# -----------------------------

def haversine_miles(lat1, lon1, lat2, lon2):
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return np.nan

    earth_radius_miles = 3958.8

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_miles * c


# -----------------------------
# 10. Calculate travel distance
# -----------------------------

analysis["travel_distance_miles"] = analysis.apply(
    lambda row: 0
    if row["home_away"] == "home"
    else haversine_miles(
        row["home_lat"],
        row["home_lon"],
        row["lat"],
        row["lon"]
    ),
    axis=1
)


# -----------------------------
# 11. Create travel bins
# -----------------------------

analysis["travel_bin"] = pd.cut(
    analysis["travel_distance_miles"],
    bins=[-1, 0, 500, 1000, 1500, 2500, np.inf],
    labels=[
        "Home",
        "0-500",
        "500-1000",
        "1000-1500",
        "1500-2500",
        "2500+"
    ]
)


# -----------------------------
# 12. Travel-distance summary
# -----------------------------

travel_summary = (
    analysis
    .dropna(subset=["travel_distance_miles"])
    .groupby("travel_bin", observed=True)
    .agg(
        team_games=("game_id", "count"),
        avg_new_injuries=("new_injuries", "mean"),
        median_new_injuries=("new_injuries", "median")
    )
    .reset_index()
)

print("\n=== INJURY VS TRAVEL DISTANCE ===")
print(travel_summary)


# Pearson correlation for away games only
away_analysis = analysis[
    (analysis["home_away"] == "away") &
    (analysis["travel_distance_miles"].notna())
].copy()

travel_corr = away_analysis[
    ["travel_distance_miles", "new_injuries"]
].corr().iloc[0, 1]

print("\nCorrelation between travel distance and injured players:")
print(round(travel_corr, 4))


# ============================================================
# PART B: STADIUM LOCATION
# ============================================================

# -----------------------------
# 13. Stadium-level injury summary
# -----------------------------

stadium_summary = (
    analysis
    .dropna(subset=["stadium_name"])
    .groupby(
        [
            "stadium_id",
            "stadium_name",
            "city",
            "state"
        ]
    )
    .agg(
        team_games=("game_id", "count"),
        total_new_injuries=("new_injuries", "sum"),
        avg_new_injuries=("new_injuries", "mean")
    )
    .reset_index()
)


# Keep stadiums with enough observations
stadium_summary_filtered = (
    stadium_summary[
        stadium_summary["team_games"] >= 20
    ]
    .sort_values(
        "avg_new_injuries",
        ascending=False
    )
)


print("\n=== STADIUMS WITH HIGHEST AVERAGE INJURY COUNTS ===")
print(
    stadium_summary_filtered[
        [
            "stadium_name",
            "city",
            "state",
            "team_games",
            "avg_new_injuries"
        ]
    ].head(15)
)


# -----------------------------
# 14. State-level injury summary
# -----------------------------

state_summary = (
    analysis
    .dropna(subset=["state"])
    .groupby("state")
    .agg(
        team_games=("game_id", "count"),
        avg_new_injuries=("new_injuries", "mean")
    )
    .reset_index()
    .sort_values(
        "avg_new_injuries",
        ascending=False
    )
)

print("\n=== INJURY BY STADIUM STATE ===")
print(state_summary.head(15))


# -----------------------------
# 15. Surface and roof bonus
# -----------------------------

surface_summary = (
    analysis
    .dropna(subset=["surface_type"])
    .groupby("surface_type")
    .agg(
        team_games=("game_id", "count"),
        avg_new_injuries=("new_injuries", "mean")
    )
    .reset_index()
    .sort_values(
        "avg_new_injuries",
        ascending=False
    )
)

print("\n=== INJURY BY SURFACE TYPE ===")
print(surface_summary)


roof_summary = (
    analysis
    .dropna(subset=["roof_type"])
    .groupby("roof_type")
    .agg(
        team_games=("game_id", "count"),
        avg_new_injuries=("new_injuries", "mean")
    )
    .reset_index()
    .sort_values(
        "avg_new_injuries",
        ascending=False
    )
)

print("\n=== INJURY BY ROOF TYPE ===")
print(roof_summary)


# -----------------------------
# 16. Save outputs
# -----------------------------

analysis.to_csv(
    "Data/team_game_full_analysis.csv",
    index=False
)

travel_summary.to_csv(
    "Data/travel_distance_summary.csv",
    index=False
)

stadium_summary_filtered.to_csv(
    "Data/stadium_injury_summary.csv",
    index=False
)

state_summary.to_csv(
    "Data/state_injury_summary.csv",
    index=False
)

surface_summary.to_csv(
    "Data/surface_injury_summary.csv",
    index=False
)

roof_summary.to_csv(
    "Data/roof_injury_summary.csv",
    index=False
)


print("\n=== FILES SAVED ===")
print("Data/team_game_full_analysis.csv")
print("Data/travel_distance_summary.csv")
print("Data/stadium_injury_summary.csv")
print("Data/state_injury_summary.csv")
print("Data/surface_injury_summary.csv")
print("Data/roof_injury_summary.csv")