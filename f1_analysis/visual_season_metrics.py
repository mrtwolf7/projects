import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv("df_races_metrics.csv")
df_drivers_standings = pd.read_csv("df_drivers_standings.csv")
df_constructors_standings = pd.read_csv("df_constructors_standings.csv")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "F1 Race Metrics"

# Get list of available years
years = sorted(df['year'].unique())

# App layout
app.layout = html.Div([
    html.Div([
        html.Label("Select Year:", style={"marginRight": "10px"}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in years],
            value=years[0],
            clearable=False,
            style={'width': '200px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px 20px'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id='driver-ratio'), width=6),
        dbc.Col(dcc.Graph(id='constructor-ratio'), width=6),
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='driver-wins'), width=6),
        dbc.Col(dcc.Graph(id='constructor-wins'), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='avg-gap-timeseries'), width=6),
        dbc.Col(dcc.Graph(id='avg-gap-dist'), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='pos-change-timeseries'), width=6),
        dbc.Col(dcc.Graph(id='pos-change-dist'), width=6),
    ])
])

# Callbacks
@app.callback(
    Output('driver-ratio', 'figure'),
    Output('constructor-ratio', 'figure'),    
    Output('driver-wins', 'figure'),
    Output('constructor-wins', 'figure'),
    Output('avg-gap-timeseries', 'figure'),
    Output('avg-gap-dist', 'figure'),
    Output('pos-change-timeseries', 'figure'),
    Output('pos-change-dist', 'figure'),
    Input('year-dropdown', 'value')
)
def update_graphs(selected_year):
    dff = df[df['year'] == selected_year]
    dff_drivers_standings = df_drivers_standings[df_drivers_standings['year'] == selected_year]
    dff_constructors_standings = df_constructors_standings[df_constructors_standings['year'] == selected_year]


    # Pie chart: driver points ratio
    fig_driver_ratio = px.pie(dff_drivers_standings, values='points', names='driver_id', title='Drivers points')
    fig_driver_ratio.update_traces(textposition='outside')

    # Pie chart: constructor points ratio
    fig_constructor_ratio = px.pie(dff_constructors_standings, values='points', names='constructor_id', title='Constructor points')
    fig_constructor_ratio.update_traces(textposition='outside')

    # Bar chart: driver wins
    driver_counts = dff['winner'].value_counts().reset_index()
    driver_counts.columns = ['driver', 'wins']
    fig_driver_wins = px.bar(driver_counts, x='driver', y='wins', title='Driver Victories', text='wins')
    fig_driver_wins.update_traces(textposition='outside')

    # Bar chart: constructor wins
    constructor_counts = dff['constructor'].value_counts().reset_index()
    constructor_counts.columns = ['constructor', 'wins']
    fig_constructor_wins = px.bar(constructor_counts, x='constructor', y='wins', title='Constructor Victories', text='wins')
    fig_constructor_wins.update_traces(textposition='outside')

    # Timeseries: average gap
    fig_avg_gap_ts = px.line(dff, x='track_name', y='average_gap', title='Average Gap by Track')
    fig_avg_gap_ts.update_xaxes(tickangle=45)

    # Distribution: average gap
    fig_avg_gap_dist = px.histogram(dff, x='average_gap', nbins=10, title='Distribution of Average Gap')

    # Timeseries: position change
    fig_pos_change_ts = px.line(dff, x='track_name', y='position_change', title='Position Change by Track')
    fig_pos_change_ts.update_xaxes(tickangle=45)

    # Distribution: position change
    fig_pos_change_dist = px.histogram(dff, x='position_change', nbins=10, title='Distribution of Position Change')

    return (
        fig_driver_ratio,
        fig_constructor_ratio,
        fig_driver_wins,
        fig_constructor_wins,
        fig_avg_gap_ts,
        fig_avg_gap_dist,
        fig_pos_change_ts,
        fig_pos_change_dist
    )


if __name__ == '__main__':
    app.run_server(debug=True)
