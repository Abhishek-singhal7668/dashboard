import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Read the cleaned data
df = pd.read_csv('data.csv')

# Treat 'Month Year' as a categorical variable and sort it
df['Month Year'] = pd.Categorical(df['Month Year'], categories=[
    'Jan-2024', 'Feb-2024', 'Mar-2024', 'Apr-2024', 'May-2024', 'Jun-2024', 
    'Jul-2024', 'Aug-2024', 'Sep-2024', 'Oct-2024', 'Nov-2024', 'Dec-2024'], ordered=True)
df = df.sort_values('Month Year')

# Melt the DataFrame to long format
df_melted = df.melt(id_vars=['Month Year', 'Rating', 'Locality'], 
                    value_vars=['Trip advisor', 'Airbnb', 'MMT/Goibibo', 'Agoda', 'Booking.Com'],
                    var_name='OTA Name', value_name='Count')

# Drop rows with missing values
df_melted = df_melted.dropna(subset=['Count'])

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("OTA Performance Dashboard", className="text-center", style={'color': 'white'})
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='property-filter',
                options=[{'label': prop, 'value': prop} for prop in sorted(df['Locality'].dropna().unique())],
                multi=True,
                placeholder="Select Properties",
                style={'color': 'black'}
            ),
            dcc.Dropdown(
                id='ota-filter',
                options=[{'label': ota, 'value': ota} for ota in ['Trip advisor', 'Airbnb', 'MMT/Goibibo', 'Agoda', 'Booking.Com']],
                multi=True,
                placeholder="Select OTAs",
                style={'color': 'black'}
            ),
            dcc.Dropdown(
                id='month-filter',
                options=[{'label': month, 'value': month} for month in df['Month Year'].cat.categories],
                multi=True,
                placeholder="Select Months",
                style={'color': 'black'}
            ),
        ], width=4),
        dbc.Col([
            dcc.Graph(id='line-chart', config={'displayModeBar': False}),
            dcc.Graph(id='bar-chart', config={'displayModeBar': False}),
            dcc.Graph(id='heatmap', config={'displayModeBar': False}),
            dcc.Graph(id='pie-chart', config={'displayModeBar': False}),
            dcc.Graph(id='comparative-bar-chart', config={'displayModeBar': False})
        ], width=8)
    ])
], fluid=True)

# Callbacks to update charts based on filters
@app.callback(
    Output('line-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('heatmap', 'figure'),
    Output('pie-chart', 'figure'),
    Output('comparative-bar-chart', 'figure'),
    Input('property-filter', 'value'),
    Input('ota-filter', 'value'),
    Input('month-filter', 'value')
)
def update_charts(selected_properties, selected_otas, selected_months):
    filtered_df = df_melted
    if selected_properties:
        filtered_df = filtered_df[filtered_df['Locality'].isin(selected_properties)]
    if selected_otas:
        filtered_df = filtered_df[filtered_df['OTA Name'].isin(selected_otas)]
    if selected_months:
        filtered_df = filtered_df[filtered_df['Month Year'].isin(selected_months)]

    line_chart = px.line(filtered_df, x='Month Year', y='Count', color='Rating', 
                         line_group='OTA Name', title='Monthly Star Rating Trends',
                         hover_name='OTA Name', hover_data={'Rating': True, 'Locality': True, 'Count': True})
    bar_chart = px.bar(filtered_df, x='OTA Name', y='Count', color='Rating', 
                       barmode='group', title='Total Star Ratings per OTA')
    heatmap = px.density_heatmap(filtered_df, x='Locality', y='OTA Name', z='Count', 
                                 title='Property-Wise Performance')
    pie_chart = px.pie(filtered_df, names='Rating', values='Count', 
                       title='Distribution of Star Ratings')
    comparative_bar_chart = px.bar(filtered_df, x='Locality', y='Count', color='Rating', 
                                   barmode='group', title='Comparative Performance of Properties')

    line_chart.update_layout(template='plotly_dark')
    bar_chart.update_layout(template='plotly_dark')
    heatmap.update_layout(template='plotly_dark')
    pie_chart.update_layout(template='plotly_dark')
    comparative_bar_chart.update_layout(template='plotly_dark')

    return line_chart, bar_chart, heatmap, pie_chart, comparative_bar_chart

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
