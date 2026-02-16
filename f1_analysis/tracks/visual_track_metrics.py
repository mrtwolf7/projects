import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv("../df_races_metrics.csv")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "F1 Tracks Metrics"

# Get list of available tracks
tracks = sorted(df['track_name'].unique())

# App layout
app.layout = html.Div([
    html.Div([
        html.Label("Select Track:", style={"marginRight": "10px"}),
        dcc.Dropdown(
            id='track-dropdown',
            options=[{'label': str(track_name), 'value': track_name} for track_name in tracks],
            value=tracks[0],
            clearable=False,
            style={'width': '200px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px 20px'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id='driver-victories'), width=6),
        dbc.Col(dcc.Graph(id='constructor-victories'), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='avg-gap-timeseries'), width=6),
        dbc.Col(dcc.Graph(id='avg-gap-dist'), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='pos-change-timeseries'), width=6),
        dbc.Col(dcc.Graph(id='pos-change-dist'), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='grid-timeseries'), width=6),
        dbc.Col(dcc.Graph(id='grid-dist'), width=6),
    ])
])

# Callbacks
@app.callback(
    Output('driver-victories', 'figure'),
    Output('constructor-victories', 'figure'),
    Output('avg-gap-timeseries', 'figure'),
    Output('avg-gap-dist', 'figure'),
    Output('pos-change-timeseries', 'figure'),
    Output('pos-change-dist', 'figure'),
    Output('grid-timeseries', 'figure'),
    Output('grid-dist', 'figure'),
    Input('track-dropdown', 'value')
)
def update_graphs(selected_track):
    dff = df[df['track_name'] == selected_track]

    # Bar chart: driver victories
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
    fig_avg_gap_ts = px.line(dff, x='year', y='average_gap', title='Average Gap by Year')
    fig_avg_gap_ts.update_xaxes(tickangle=45)

    # Distribution: average gap
    fig_avg_gap_dist = px.histogram(dff, x='average_gap', nbins=10, title='Distribution of Average Gap')

    # Timeseries: position change
    fig_pos_change_ts = px.line(dff, x='year', y='position_change', title='Position Change by Year')
    fig_pos_change_ts.update_xaxes(tickangle=45)

    # Distribution: position change
    fig_pos_change_dist = px.histogram(dff, x='position_change', nbins=10, title='Distribution of Position Change')

    # Timeseries: position change
    fig_grid_ts = px.line(dff, x='year', y='grid', title='Grid Position of Winners by Year')
    fig_grid_ts.update_xaxes(tickangle=45)

    # Bar chart: grid position
    grid_counts = dff['grid'].value_counts().reset_index()
    grid_counts.columns = ['grid', 'wins']
    #fig_constructor_ratio = px.pie(dff_constructors_standings, values='points', names='constructor_id', title='Constructor points')
    #fig_constructor_ratio.update_traces(textposition='outside')
    fig_grid_wins = px.pie(grid_counts, values='wins', names='grid', title='Grid Victories')
    fig_grid_wins.update_traces(textposition='outside')
    #fig_grid_wins = px.bar(grid_counts, x='grid', y='wins', title='Grid Victories', text='wins')
    #fig_grid_wins.update_traces(textposition='outside')



    return (
        fig_driver_wins,
        fig_constructor_wins,
        fig_avg_gap_ts,
        fig_avg_gap_dist,
        fig_pos_change_ts,
        fig_pos_change_dist,
        fig_grid_ts,
        fig_grid_wins
    )



if __name__ == '__main__':
    app.run_server(debug=True)