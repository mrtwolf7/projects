import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv("df_races_metrics.csv")
df_drivers_standings = pd.read_csv("df_drivers_standings.csv")
df_constructors_standings = pd.read_csv("df_constructors_standings.csv")
df_all = pd.read_csv("df_season_metrics.csv")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "F1 Race Metrics"

# Get list of available years
years = sorted(df['year'].unique())

#App layout
app.layout = html.Div([
    html.Div([
        html.Label("Select Year:", style={"marginRight": "10px"}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': 'All', 'value': 'all'}] + [{'label': str(year), 'value': year} for year in years],
            value=years[0],
            clearable=False,
            style={'width': '200px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px 20px'}),

    html.Div(id='graphs-container')
])

# Callbacks
@app.callback(
    Output('graphs-container', 'children'),
    Input('year-dropdown', 'value')
)
def render_layout(selected_year):
    if selected_year == 'all':
        # Plot for 'All'
        fig_avg_gap_all = px.line(df_all, x='year', y='average_gaps', title='Average Gap Over Years')
        fig_pos_change_all = px.line(df_all, x='year', y='average_position_change', title='Average Position Change Over Years')
        fig_gini_driver_all = px.line(df_all, x='year', y='winner_drivers_gini', title='Gini Index for Driver Winners')
        fig_gini_constructor_all = px.line(df_all, x='year', y='winner_constructors_gini', title='Gini Index for Constructor Winners')

        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_avg_gap_all), width=6),
                dbc.Col(dcc.Graph(figure=fig_pos_change_all), width=6)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_gini_driver_all), width=6),
                dbc.Col(dcc.Graph(figure=fig_gini_constructor_all), width=6)
            ])
        ])

    else:
        dff = df[df['year'] == selected_year]
        dff_drivers_standings = df_drivers_standings[df_drivers_standings['year'] == selected_year]
        dff_constructors_standings = df_constructors_standings[df_constructors_standings['year'] == selected_year]

        fig_driver_ratio = px.pie(dff_drivers_standings, values='points', names='driver_id', title='Drivers points')
        fig_constructor_ratio = (
            px.pie(dff_constructors_standings, values='points', names='constructor_id', title='Constructor points')
            if not dff_constructors_standings.empty else
            px.pie(names=["No data"], values=[1], title="Constructor points")
        )

        driver_counts = dff['winner'].value_counts().reset_index()
        driver_counts.columns = ['driver', 'wins']
        fig_driver_wins = px.bar(driver_counts, x='driver', y='wins', title='Driver Victories', text='wins')

        constructor_counts = dff['constructor'].value_counts().reset_index()
        constructor_counts.columns = ['constructor', 'wins']
        fig_constructor_wins = px.bar(constructor_counts, x='constructor', y='wins', title='Constructor Victories', text='wins')

        fig_avg_gap_ts = px.line(dff, x='track_name', y='average_gap', title='Average Gap by Track')
        fig_avg_gap_dist = px.histogram(dff, x='average_gap', nbins=10, title='Distribution of Average Gap')

        fig_pos_change_ts = px.line(dff, x='track_name', y='position_change', title='Position Change by Track')
        fig_pos_change_dist = px.histogram(dff, x='position_change', nbins=10, title='Distribution of Position Change')

        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_driver_ratio), width=6),
                dbc.Col(dcc.Graph(figure=fig_constructor_ratio), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_driver_wins), width=6),
                dbc.Col(dcc.Graph(figure=fig_constructor_wins), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_avg_gap_ts), width=6),
                dbc.Col(dcc.Graph(figure=fig_avg_gap_dist), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_pos_change_ts), width=6),
                dbc.Col(dcc.Graph(figure=fig_pos_change_dist), width=6),
            ])
        ])



if __name__ == '__main__':
    app.run_server(debug=True)
