import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the data
df = pd.read_csv("weather.csv")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Easter Mondays stats"

# Get list of available citie
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
        dbc.Col(dcc.Graph(id='rainy-months'), width=12),
        dbc.Col(dcc.Graph(id='temp-months'), width=12)
    ])
])

# Callbacks
@app.callback(
    Output('rainy-years', 'figure'),
    Output('rainy-months', 'figure'),
    Output('temp-months', 'figure'),
    Input('city-dropdown', 'value')
)
def update_graphs(selected_city):
    dff = df[df['city'] == selected_city]
    dff_grouped = (
        dff.groupby(['year', 'easter_monday'], as_index=False).agg({'rain_mm': 'mean'})
    )

    dff['month_day_num'] = pd.to_datetime(dff['day']).dt.strftime('%m%d').astype(int)
    dff['month_day_str'] = dff['month_day_num'].apply(lambda x: f"{str(x)[:1]}-{str(x)[1:]}")
    dff_grouped_month = (
        dff.groupby(['month_day_num', 'month_day_str', 'easter_monday'], as_index=False)
        .agg({'rain_mm': 'mean', 'temperature_c': 'mean'})
        .sort_values('month_day_num')  # ensures calendar order
    )
    df_line = dff_grouped_month[dff_grouped_month['easter_monday'] == False]
    df_dots = dff_grouped_month[dff_grouped_month['easter_monday'] == True]


    # Bar chart: year rainy days
    fig_rain_years = px.bar(dff_grouped, x='year', y='rain_mm', title='Rain Over Years', color='easter_monday', barmode='group')
    fig_rain_years.update_traces(textposition='outside')
    fig_rain_years.update_xaxes(tickmode='linear', dtick=1, tickangle=45)

    # Timeseries: month rainy days
    fig_rain_month_ts = go.Figure()
    fig_rain_month_ts.add_trace(go.Scatter(
        x=df_line['month_day_str'],
        y=df_line['rain_mm'],
        mode='lines',
        name='Avg Rain (Non-Easter Monday)'
    ))
    fig_rain_month_ts.add_trace(go.Scatter(
        x=df_dots['month_day_str'],
        y=df_dots['rain_mm'],
        mode='markers+text',
        name='Easter Monday',
        marker=dict(size=10, color='red'),
        text=df_dots['rain_mm'],
        textposition='top center'
    ))
    fig_rain_month_ts.update_layout(
        title='Rain mm Over Days of the Year',
        xaxis_title='Day (MM-DD)',
        yaxis_title='Rain (mm)',
    )
    fig_rain_month_ts.update_xaxes(
        tickangle=45,
        type = 'category'
        )

    # Timeseries: month temperature days
    fig_temp_month_ts = go.Figure()
    fig_temp_month_ts.add_trace(go.Scatter(
        x=df_line['month_day_str'],
        y=df_line['temperature_c'],
        mode='lines',
        name='Avg Temperature (Non-Easter Monday)'
    ))
    fig_temp_month_ts.add_trace(go.Scatter(
        x=df_dots['month_day_str'],
        y=df_dots['temperature_c'],
        mode='markers+text',
        name='Easter Monday',
        marker=dict(size=10, color='red'),
        text=df_dots['temperature_c'],
        textposition='top center'
    ))
    fig_temp_month_ts.update_layout(
        title='Temperature Over Days of the Year',
        xaxis_title='Day (MM-DD)',
        yaxis_title='Temperature (C)',
    )
    fig_temp_month_ts.update_xaxes(
        tickangle=45,
        type = 'category'
        )

    return (
        fig_rain_years,
        fig_rain_month_ts,
        fig_temp_month_ts
    )



if __name__ == '__main__':
    app.run_server(debug=True)