import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.express as px

# -------------------------------
# 1. Load data
# -------------------------------
df = pd.read_csv("fpl_predicted_form.csv")

# -------------------------------
# 2. Initialize app
# -------------------------------
app = dash.Dash(__name__)

# -------------------------------
# 3. Layout
# -------------------------------
app.layout = html.Div([
    html.H1("FPL Predicted Form Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label("Select Team:"),
            dcc.Dropdown(
                options=[{"label": t, "value": t} for t in sorted(df["team_name"].unique())],
                id="team_filter",
                placeholder="All Teams",
                multi=True
            )
        ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top"}),

        html.Div([
            html.Label("Select Position:"),
            dcc.Dropdown(
                options=[{"label": p, "value": p} for p in sorted(df["position"].unique())],
                id="position_filter",
                placeholder="All Positions",
                multi=True
            )
        ], style={"width": "30%", "display": "inline-block", "marginLeft": "2%"}),

        html.Div([
            html.Label("Max Fixture Difficulty (next 5):"),
            dcc.Slider(
                min=df["next5_avg_difficulty"].min(),
                max=df["next5_avg_difficulty"].max(),
                step=0.1,
                value=df["next5_avg_difficulty"].max(),
                marks={i: str(i) for i in range(1, 6)},
                id="difficulty_filter"
            )
        ], style={"width": "35%", "display": "inline-block", "marginLeft": "2%"})
    ], style={"marginBottom": "30px"}),

    dcc.Graph(id="scatter_fig"),
    dcc.Graph(id="bar_diff_fig"),

    html.H2("Filtered Player Data"),
    dash_table.DataTable(
        id="player_table",
        columns=[{"name": i, "id": i} for i in [
            "second_name", "team_name", "position", "form", "predicted_form",
            "form_diff", "next5_avg_difficulty"
        ]],
        page_size=20,
        sort_action="native",
        filter_action="native"
    )
])

# -------------------------------
# 4. Callbacks
# -------------------------------
@app.callback(
    [Output("scatter_fig", "figure"),
     Output("bar_diff_fig", "figure"),
     Output("player_table", "data")],
    [Input("team_filter", "value"),
     Input("position_filter", "value"),
     Input("difficulty_filter", "value")]
)
def update_dashboard(selected_teams, selected_positions, max_difficulty):
    filtered = df.copy()

    if selected_teams:
        filtered = filtered[filtered["team_name"].isin(selected_teams)]
    if selected_positions:
        filtered = filtered[filtered["position"].isin(selected_positions)]
    if max_difficulty:
        filtered = filtered[filtered["next5_avg_difficulty"] <= max_difficulty]

    # Scatter: actual vs predicted form
    scatter_fig = px.scatter(
        filtered,
        x="form", y="predicted_form",
        color="team_name",
        hover_data=["second_name", "team_name", "position", "next5_avg_difficulty"],
        title="Actual vs Predicted Form (Filtered)"
    )

    # Bar: top 20 predicted improvements
    bar_diff_fig = px.bar(
        filtered.sort_values("form_diff", ascending=False).head(20),
        x="second_name", y="form_diff",
        color="team_name",
        title="Top 20 Players by Predicted Form Improvement (Predicted - Actual)",
        hover_data=["team_name", "position", "predicted_form", "form", "next5_avg_difficulty"]
    )

    # Table
    table_data = filtered.sort_values("predicted_form", ascending=False).to_dict("records")

    return scatter_fig, bar_diff_fig, table_data

# -------------------------------
# 5. Run server
# -------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
