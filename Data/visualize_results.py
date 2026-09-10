import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# Preliminary visualizations:
# NFL Injuries vs Travel Distance / Stadium Location
# ============================================================

OUTPUT_DIR = Path("figures/preliminary")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load outputs from analysis script
analysis = pd.read_csv("Data/team_game_full_analysis.csv")
travel = pd.read_csv("Data/travel_distance_summary.csv")
stadiums = pd.read_csv("Data/stadium_injury_summary.csv")
surface = pd.read_csv("Data/surface_injury_summary.csv")


# ============================================================
# 1. Average injury-report count by travel-distance category
# ============================================================

plt.figure(figsize=(10, 6))

bars = plt.bar(
    travel["travel_bin"],
    travel["avg_injured_players"]
)

plt.title(
    "Preliminary: Injury-Report Counts by Travel Distance",
    fontsize=15
)

plt.xlabel("Travel distance")
plt.ylabel("Average players on injury report")

plt.ylim(0, max(travel["avg_injured_players"]) * 1.15)

for bar, value in zip(bars, travel["avg_injured_players"]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.12,
        f"{value:.2f}",
        ha="center",
        fontsize=10
    )

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "injuries_by_travel_distance.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ============================================================
# 2. Away-game travel distance vs injury-report count
# ============================================================

away = analysis[
    (analysis["home_away"] == "away") &
    (analysis["travel_distance_miles"].notna())
].copy()

x = away["travel_distance_miles"].to_numpy()
y = away["injured_players"].to_numpy()

correlation = np.corrcoef(x, y)[0, 1]

# Regression line
slope, intercept = np.polyfit(x, y, 1)

x_line = np.linspace(x.min(), x.max(), 200)
y_line = slope * x_line + intercept

plt.figure(figsize=(10, 6))

plt.scatter(
    x,
    y,
    alpha=0.18,
    s=18
)

plt.plot(
    x_line,
    y_line,
    linewidth=2
)

plt.title(
    "Preliminary: Travel Distance Shows Little Relationship with Injury Reports",
    fontsize=14
)

plt.xlabel("Away-game travel distance (miles)")
plt.ylabel("Players on weekly injury report")

plt.text(
    0.03,
    0.94,
    f"Pearson r = {correlation:.3f}",
    transform=plt.gca().transAxes,
    fontsize=11,
    verticalalignment="top"
)

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "travel_distance_injury_scatter.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ============================================================
# 3. Top 10 stadiums by average injury-report count
# ============================================================

top10 = (
    stadiums
    .sort_values("avg_injured_players", ascending=False)
    .head(10)
    .sort_values("avg_injured_players")
)

plt.figure(figsize=(11, 7))

bars = plt.barh(
    top10["stadium_name"],
    top10["avg_injured_players"]
)

plt.title(
    "Preliminary: Stadiums with Highest Average Injury-Report Counts",
    fontsize=14
)

plt.xlabel("Average players on injury report")
plt.ylabel("Stadium")

for bar, value in zip(bars, top10["avg_injured_players"]):
    plt.text(
        bar.get_width() + 0.05,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}",
        va="center",
        fontsize=9
    )

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "top10_stadium_injury_counts.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ============================================================
# 4. Grass vs Turf
# ============================================================

surface_clean = (
    surface[
        surface["surface_type"].isin(["Grass", "Turf"])
    ]
    .copy()
)

plt.figure(figsize=(7, 6))

bars = plt.bar(
    surface_clean["surface_type"],
    surface_clean["avg_injured_players"]
)

plt.title(
    "Preliminary: Injury-Report Counts by Playing Surface",
    fontsize=14
)

plt.xlabel("Surface")
plt.ylabel("Average players on injury report")

plt.ylim(
    0,
    max(surface_clean["avg_injured_players"]) * 1.15
)

for bar, value in zip(
    bars,
    surface_clean["avg_injured_players"]
):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.12,
        f"{value:.2f}",
        ha="center",
        fontsize=11
    )

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "grass_vs_turf_injury_counts.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


print("=== VISUALIZATIONS CREATED ===")
print(OUTPUT_DIR / "injuries_by_travel_distance.png")
print(OUTPUT_DIR / "travel_distance_injury_scatter.png")
print(OUTPUT_DIR / "top10_stadium_injury_counts.png")
print(OUTPUT_DIR / "grass_vs_turf_injury_counts.png")
print(f"\nAway-game travel correlation: {correlation:.4f}")