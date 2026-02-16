import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the data
df = pd.read_csv("weather.csv")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Easter Mondays weather stats"

# Get list of available cities
cities = sorted(df['city'].unique())

# App layout
app.layout = html.Div([
    html.Div([
        html.Label("Select City:", style={"marginRight": "10px"}),
        dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': 'All', 'value': 'all'}]+[{'label': str(city), 'value': city} for city in cities],
            value=cities[0],
            clearable=False,
            style={'width': '200px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px 20px'}),

    html.Div(id='graphs-container')
])

# Callbacks
@app.callback(
    Output('graphs-container', 'children'),
    Input('city-dropdown', 'value')
)
def update_graphs(selected_city):
    if selected_city == 'all':
        df_east_mon = df[df['easter_monday'] == True]
        df_normal = df[df['easter_monday'] == False]
        easter_monday_counts = df_east_mon.groupby('city').size().reset_index(name='total_easter_mondays')


        df_summary = (
            pd.merge(
                df_east_mon.groupby('city').agg(
                    rainy_easter_count=('rain_mm', lambda x: (x > 0).sum()),
                    avg_rain_easter=('rain_mm', 'mean'),
                    avg_temp_easter=('temperature_c', 'mean')
                ),
                df_normal.groupby('city').agg(
                    avg_rain_normal=('rain_mm', 'mean'),
                    avg_temp_normal=('temperature_c', 'mean')
                ),
                on='city'
            )
            .assign(
                rain_diff=lambda d: d['avg_rain_easter'] - d['avg_rain_normal'],
                temp_diff=lambda d: d['avg_temp_easter'] - d['avg_temp_normal']
            )
            .reset_index()
        )
        df_summary = df_summary.merge(easter_monday_counts, on='city')

        df_summary_year = (
            pd.merge(
                df_east_mon.groupby(['city', 'year']).agg(
                    avg_rain_easter_y=('rain_mm', 'mean'),
                    avg_temp_easter_y=('temperature_c', 'mean')
                ),
                df_normal.groupby(['city', 'year']).agg(
                    avg_rain_normal_y=('rain_mm', 'mean'),
                    avg_temp_normal_y=('temperature_c', 'mean')
                ),
                on=['city', 'year']
            )
            .assign(
                rain_diff_y=lambda d: d['avg_rain_easter_y'] - d['avg_rain_normal_y'],
                temp_diff_y=lambda d: d['avg_temp_easter_y'] - d['avg_temp_normal_y']
            )
            .reset_index()
        )        

        # Bar chart: count cities with most rainy easter Mondays
        fig_rain_cities = px.bar(df_summary, x='city', y='rainy_easter_count', title='Count of rainy Easter Mondays', barmode='group')
        fig_rain_cities.update_traces(
            textposition='outside',
            hovertemplate=(
                'City: %{x}<br>' +
                'Rainy Easter Mondays: %{y}<br>' +
                'Total Easter Mondays: %{customdata[0]}'
            ),
            customdata=df_summary[['total_easter_mondays']].values
        )
        fig_rain_cities.update_xaxes(tickmode='linear', dtick=1, tickangle=45)

        # Bar chart: avergae temperature of cities on easter Mondays
        fig_avg_temp_cities = px.bar(df_summary, x='city', y='avg_temp_easter', title='Average temperature on Easter Mondays', barmode='group')
        fig_avg_temp_cities.update_traces(textposition='outside')
        fig_avg_temp_cities.update_xaxes(tickmode='linear', dtick=1, tickangle=45)

        # Time series: rain (mm) difference
        fig_rain_diff_y = go.Figure()
        for city in df_summary_year['city'].unique():
            df_city = df_summary_year[df_summary_year['city'] == city]
            fig_rain_diff_y.add_trace(go.Scatter(
                x=df_city['year'],
                y=df_city['rain_diff_y'],
                mode='lines+markers',
                name=city
            ))

        fig_rain_diff_y.update_layout(
            title='Rain Difference Between Easter Mondays and Normal Days (by Year)',
            xaxis_title='Year',
            yaxis_title='Rain Difference (mm)'
        )

        # Time series: temperature difference
        fig_temp_diff_y = go.Figure()
        for city in df_summary_year['city'].unique():
            df_city = df_summary_year[df_summary_year['city'] == city]
            fig_temp_diff_y.add_trace(go.Scatter(
                x=df_city['year'],
                y=df_city['temp_diff_y'],
                mode='lines+markers',
                name=city  # this creates a legend entry per city
            ))

        fig_temp_diff_y.update_layout(
            title='Temperature Difference Between Easter Mondays and Normal Days (by Year)',
            xaxis_title='Year',
            yaxis_title='Temperature Difference (°C)'
        )
        
        return dbc.Container([   
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_rain_cities), width=12),
                dbc.Col(dcc.Graph(figure=fig_avg_temp_cities), width=12),
                dbc.Col(dcc.Graph(figure=fig_rain_diff_y), width=12),
                dbc.Col(dcc.Graph(figure=fig_temp_diff_y), width=12)
            ])
        ])


    else:    
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

        return dbc.Container([   
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_rain_years), width=12),
                dbc.Col(dcc.Graph(figure=fig_rain_month_ts), width=12),
                dbc.Col(dcc.Graph(figure=fig_temp_month_ts), width=12)
            ])
        ])



if __name__ == '__main__':
    app.run_server(debug=True)