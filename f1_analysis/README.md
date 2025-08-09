# F1 Analysis
This folder contains multiple scripts and visuals to analyse and just have fun with F1 data.
All of this started because I wanted to try to answer questions like 'Is it true that F1 is less fun these days?' or 'How predictable F1 is?', 'Does it depend on the track?'.

## Metrics
In order to provide a partial answer to these questions I have collected metrics querying the data from ergast API from every single race where data was available from the start of F1 in 1950 until 2024.

### What metrics am I using?
Starting from the collection of the most immediate metrics like drivers, constructors, winners, grid positions, overall time I have developed two metrics to get an approximate idea of the boredom of a race:
* average gap (s): for every race, the average gap between the top 5 drivers, computed as the time difference in seconds between each consecutive position.
* position change: for every race, the sum of the position change from the starting grid for the top 5 drivers.

## Structure
There are four main scripts:
* main_season_races.py saves metrics to two csv files: df_races_metrics.csv and df_season_metrics.csv;
* main_season_standings.py saves metrics to two csv files: df_constructor_standings.csv and df_drivers_standings.csv;
* visual_season_metrics.py takes all of the four csvs in input to generate visuals in a dash interactive interface about every different season;
* visual_track_metrics.py takes df_races_metrics.csv in input to generate visuals in a dash interactive interface about every different track.

To open the dash interactive interfaces, just run the two visual_* python files, those will open the interfaces in the browser.

## What's next?
I want to build a model to predict the race winners (at least): the idea is to train the model on a richer dataset (so I will have to use a different API), using all the data avaialble for every race weekend. This is to ensure not just to predict race winner based on qualifiers, but alo using at least data from FP3, usually a good indicator of the face pace.