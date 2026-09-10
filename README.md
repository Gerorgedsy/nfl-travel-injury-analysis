# nfl-travel-injury-analysis

Analyzing the common factors causing player injuries.

## Data

To load all required data, run Data/data\_load.py. To access stadium data please download the CSV from: https://github.com/greerreNFL/Stadiums/blob/main/data/stadiums.csv.



\## Preliminary Injury \& Travel Analysis



This branch contains an initial exploratory analysis of the relationship between NFL injury-report counts, travel distance, and stadium location for the 2009–2025 regular seasons.



\### Preliminary Findings



\- Travel distance shows little apparent linear relationship with weekly injury-report counts.

\- Among away games, the Pearson correlation between travel distance and injured players is approximately \*\*-0.032\*\*.

\- Injury-report counts vary more noticeably across stadiums than across travel-distance categories.

\- Turf games currently show a slightly higher average injury-report count than grass games.



\### Important Limitation



The current injury metric represents the number of unique players appearing on a team's weekly injury report. It should not yet be interpreted as the number of injuries caused during a specific game.



The next stage will refine the injury metric and improve the travel-distance calculation using season-specific team home locations.



\### Preliminary Visualizations



!\[Travel Distance Categories](figures/preliminary/injuries\_by\_travel\_distance.png)



!\[Travel Distance Scatter](figures/preliminary/travel\_distance\_injury\_scatter.png)



!\[Stadium Injury Counts](figures/preliminary/top10\_stadium\_injury\_counts.png)



!\[Grass vs Turf](figures/preliminary/grass\_vs\_turf\_injury\_counts.png)

