import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv("df_races_metrics.csv")

# Initialize Dash app
app = dash.Dash(__name__)
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

    html.Div([
        html.Div([dcc.Graph(id='driver-wins')], className='six columns'),
        html.Div([dcc.Graph(id='constructor-wins')], className='six columns'),
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='avg-gap-timeseries')], className='six columns'),
        html.Div([dcc.Graph(id='avg-gap-dist')], className='six columns'),
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='pos-change-timeseries')], className='six columns'),
        html.Div([dcc.Graph(id='pos-change-dist')], className='six columns'),
    ], className='row')
], style={'padding': '10px'})


# Callbacks
@app.callback(
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
        fig_driver_wins,
        fig_constructor_wins,
        fig_avg_gap_ts,
        fig_avg_gap_dist,
        fig_pos_change_ts,
        fig_pos_change_dist
    )


if __name__ == '__main__':
    app.run_server(debug=True)
