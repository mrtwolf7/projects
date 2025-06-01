import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv("weather.csv")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Easter Mondays stats"

# Get list of available tracks
cities = sorted(df['city'].unique())

# App layout
app.layout = html.Div([
    html.Div([
        html.Label("Select City:", style={"marginRight": "10px"}),
        dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': str(city), 'value': city} for city in cities],
            value=cities[0],
            clearable=False,
            style={'width': '200px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px 20px'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id='rainy-years'), width=12),
        #dbc.Col(dcc.Graph(id='rainy-months'), width=6),
    ])
])

# Callbacks
@app.callback(
    Output('rainy-years', 'figure'),
    #Output('rainy-months', 'figure'),
    Input('city-dropdown', 'value')
)
def update_graphs(selected_city):
    dff = df[df['city'] == selected_city]
    dff_grouped = (
        dff.groupby(['year', 'easter_monday'], as_index=False).agg({'rain_mm': 'mean'})
    )

    dff_em = dff[dff['easter_monday'] == True]
    dff_otherdays = dff[dff['easter_monday'] == False]

    # Bar chart: 
    fig_rain_years = px.bar(dff_grouped, x='year', y='rain_mm', title='Rain Over Years', color='easter_monday', barmode='group')
    fig_rain_years.update_traces(textposition='outside')
    fig_rain_years.update_xaxes(tickmode='linear', dtick=1, tickangle=45)


    return (
        fig_rain_years
    )



if __name__ == '__main__':
    app.run_server(debug=True)