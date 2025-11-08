import requests
import pandas as pd
import numpy as np
import time
import os
import json
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
BASE_URL = "https://fantasy.premierleague.com/api/"
CACHE_DIR = "player_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

BATCH_SIZE = 100        # Number of players to process per batch
SLEEP_BETWEEN_CALLS = 0.3  # seconds, to avoid rate limits

# ---------------------------------------------------------------------
# 1. Load main data
# ---------------------------------------------------------------------
bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
fixtures = pd.DataFrame(requests.get(BASE_URL + "fixtures/").json())

teams = pd.DataFrame(bootstrap['teams'])
players = pd.DataFrame(bootstrap['elements'])

# ---------------------------------------------------------------------
# 2. Identify current gameweek
# ---------------------------------------------------------------------
current_gw = next(gw['id'] for gw in bootstrap['events'] if gw['is_current'])

# ---------------------------------------------------------------------
# 3. Compute next 5 fixtures’ average difficulty per team
# ---------------------------------------------------------------------
upcoming_fixtures = fixtures[fixtures['event'] >= current_gw]
team_difficulties = []

for team_id in teams['id']:
    team_name = teams.loc[teams['id'] == team_id, 'name'].values[0]
    team_fixtures = upcoming_fixtures[
        (upcoming_fixtures['team_h'] == team_id) |
        (upcoming_fixtures['team_a'] == team_id)
    ].head(5)
    
    difficulties = []
    for _, row in team_fixtures.iterrows():
        if row['team_h'] == team_id:
            difficulties.append(row['team_h_difficulty'])
        else:
            difficulties.append(row['team_a_difficulty'])
    
    avg_diff = np.mean(difficulties) if difficulties else None
    team_difficulties.append({
        'team_id': team_id,
        'team_name': team_name,
        'next5_avg_difficulty': avg_diff
    })

team_difficulty_df = pd.DataFrame(team_difficulties)

# ---------------------------------------------------------------------
# 4. Merge with players
# ---------------------------------------------------------------------
players = players.merge(
    team_difficulty_df[['team_id', 'team_name', 'next5_avg_difficulty']],
    left_on='team', right_on='team_id', how='left'
)

# Include element_type (position) and map to readable positions
position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
players_fin = players[[
    'id', 'second_name', 'team_name', 'element_type', 'now_cost', 'total_points', 
    'minutes', 'goals_scored', 'assists', 'clean_sheets', 'bps', 'form', 'ict_index',
    'next5_avg_difficulty'
]].copy()
players_fin['position'] = players_fin['element_type'].map(position_map)
players_fin['form'] = players_fin['form'].astype(float)

# ---------------------------------------------------------------------
# 5. Function to fetch and cache player history
# ---------------------------------------------------------------------
def get_player_history(player_id):
    cache_path = os.path.join(CACHE_DIR, f"{player_id}.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    url = f"{BASE_URL}element-summary/{player_id}/"
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        data = r.json()
        with open(cache_path, "w") as f:
            json.dump(data, f)
        time.sleep(SLEEP_BETWEEN_CALLS)
        return data
    except Exception:
        return None

# ---------------------------------------------------------------------
# 6. Collect recent match history for all players (in batches)
# ---------------------------------------------------------------------
player_features = []
player_ids = players_fin['id'].tolist()

for start in range(0, len(player_ids), BATCH_SIZE):
    batch = player_ids[start:start + BATCH_SIZE]
    print(f"Processing players {start + 1}–{start + len(batch)} / {len(player_ids)} ...")
    
    for pid in batch:
        p = players_fin.loc[players_fin['id'] == pid].iloc[0]
        data = get_player_history(pid)
        if not data or not data.get('history'):
            continue
        
        history = pd.DataFrame(data['history'])
        if history.empty:
            continue
        
        recent = history.tail(5)
        avg_points_last5 = recent['total_points'].mean()
        avg_minutes_last5 = recent['minutes'].mean()
        
        player_features.append({
            'id': pid,
            'second_name': p['second_name'],
            'team_name': p['team_name'],
            'position': p['position'],
            'avg_points_last5': avg_points_last5,
            'avg_minutes_last5': avg_minutes_last5,
            'next5_avg_difficulty': p['next5_avg_difficulty'],
            'form': p['form']
        })
    
    time.sleep(1.0)

df = pd.DataFrame(player_features).dropna()

# ---------------------------------------------------------------------
# 7. Train regression model
# ---------------------------------------------------------------------
X = df[['avg_points_last5', 'avg_minutes_last5', 'next5_avg_difficulty']]
y = df['form']

model = LinearRegression().fit(X, y)
df['predicted_form'] = model.predict(X)

r2 = model.score(X, y)
print(f"\nModel R² = {r2:.3f}")
print(f"Coefficients: {dict(zip(X.columns, model.coef_))}")
print(f"Intercept: {model.intercept_:.3f}\n")

# ---------------------------------------------------------------------
# 8. Merge predictions back into full player list
# ---------------------------------------------------------------------
players_fin = players_fin.merge(
    df[['id', 'predicted_form']],
    on='id', how='left'
)

# Compute difference between predicted and actual form
players_fin['form_diff'] = players_fin['predicted_form'] - players_fin['form']

# ---------------------------------------------------------------------
# 9. Display top 20 predicted performers and save CSV
# ---------------------------------------------------------------------
top_pred = players_fin.sort_values(by='predicted_form', ascending=False).head(20)
print(top_pred[['second_name', 'team_name', 'position', 'predicted_form', 'form', 'next5_avg_difficulty']].to_string(index=False))

players_fin.to_csv("fpl_predicted_form.csv", index=False)
print("✅ Saved results to fpl_predicted_form.csv")
