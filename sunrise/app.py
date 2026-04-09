import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, filter_city, aggregate_data, add_time_strings

app = dash.Dash(__name__)
server = app.server

# Load all data once
df_all = load_data()
cities = sorted(df_all["city"].unique())

app.layout = html.Div([
    html.H1("Sunrise / Sunset Comparison"),

    html.Label("City A"),
    dcc.Dropdown(options=cities, value=cities[0], id="city_a"),

    html.Label("City B"),
    dcc.Dropdown(options=cities, value=cities[1], id="city_b"),

    html.Label("Granularity"),
    dcc.Dropdown(
        options=[
            {"label": "Day", "value": "day"},
            {"label": "Week", "value": "week"},
            {"label": "Month", "value": "month"},
        ],
        value="day",
        id="granularity"
    ),

    dcc.Graph(id="chart1"),
    dcc.Graph(id="chart2"),
])


@app.callback(
    Output("chart1", "figure"),
    Output("chart2", "figure"),
    Input("city_a", "value"),
    Input("city_b", "value"),
    Input("granularity", "value"),
)
def update_charts(city_a, city_b, granularity):

    if city_a == city_b:
        return go.Figure(), go.Figure()

    df_a = filter_city(df_all, city_a)
    df_b = filter_city(df_all, city_b)

    df_a = aggregate_data(df_a, granularity)
    df_b = aggregate_data(df_b, granularity)

    df_a = add_time_strings(df_a)
    df_b = add_time_strings(df_b)

    # -------------------------
    # Chart 1 — Daylight
    # -------------------------
    fig1 = go.Figure()

    fig1.add_bar(
        x=df_a["date"],
        y=df_a["daylight_hours"],
        name=city_a,
        customdata=df_a["daylight_str"],
        hovertemplate="Daylight: %{customdata}<extra></extra>",
    )

    fig1.add_bar(
        x=df_b["date"],
        y=df_b["daylight_hours"],
        name=city_b,
        customdata=df_b["daylight_str"],
        hovertemplate="Daylight: %{customdata}<extra></extra>",
    )

    fig1.update_layout(
        barmode="group",
        title="Daylight Hours",
        xaxis_title="Date",
        yaxis_title="Hours"
    )

    # -------------------------
    # Chart 2 — Sunset top / Sunrise bottom
    # -------------------------
    fig2 = go.Figure()

    # Sunset (top)
    fig2.add_bar(
        x=df_a["date"],
        y=df_a["sunset_hours"],
        name=f"{city_a} Sunset",
        customdata=df_a["sunset_str"],
        hovertemplate="Sunset: %{customdata}<extra></extra>",
    )

    fig2.add_bar(
        x=df_b["date"],
        y=df_b["sunset_hours"],
        name=f"{city_b} Sunset",
        customdata=df_b["sunset_str"],
        hovertemplate="Sunset: %{customdata}<extra></extra>",
    )

    # Sunrise (bottom)
    fig2.add_bar(
        x=df_a["date"],
        y=-df_a["sunrise_hours"],
        name=f"{city_a} Sunrise",
        customdata=df_a["sunrise_str"],
        hovertemplate="Sunrise: %{customdata}<extra></extra>",
    )

    fig2.add_bar(
        x=df_b["date"],
        y=-df_b["sunrise_hours"],
        name=f"{city_b} Sunrise",
        customdata=df_b["sunrise_str"],
        hovertemplate="Sunrise: %{customdata}<extra></extra>",
    )

    fig2.update_layout(
        barmode="group",
        title="Sunrise and Sunset",
        xaxis_title="Date",
        yaxis_title="Hour of Day"
    )

    fig2.update_yaxes(
        tickvals=[-20, -15, -10, -5, 0, 5, 10, 15, 20],
        ticktext=["20", "15", "10", "5", "0", "5", "10", "15", "20"]
    )

    fig2.add_hline(y=0)

    return fig1, fig2


if __name__ == "__main__":
    app.run(debug=True)