import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc  
import plotly.express as px
from dash.dependencies import Input, Output
from dash import dcc
from dash.exceptions import PreventUpdate
import base64
import io

# Load your dataset
data = pd.DataFrame({
    'Date': pd.date_range(start='1/1/2023', periods=10, freq='D'),
    'Sales': [100, 200, 150, 300, 250, 400, 350, 450, 500, 550],
    'Category': ['Electronics', 'Clothing', 'Electronics', 'Home', 'Electronics', 
                 'Clothing', 'Home', 'Clothing', 'Electronics', 'Home']
})

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define layout here or keep in the index.html file
app.layout = html.Div(id='dash-app')

# Create a bar chart for total sales by category
bar_fig = px.bar(data.groupby('Category', as_index=False).sum(), 
                 x='Category', y='Sales', title='Total Sales by Category')

# Define the layout with dropdown, line chart, bar chart, and statistics
app.layout = html.Div(children=[
    html.H1(children='Data Analysis Dashboard'),

    # File Upload
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload CSV File'),
        multiple=False  # Set to True if you want to allow multiple files
    ),
    
    html.Label('Select Category'),
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': 'All Categories', 'value': 'All'},
            {'label': 'Electronics', 'value': 'Electronics'},
            {'label': 'Clothing', 'value': 'Clothing'},
            {'label': 'Home', 'value': 'Home'}
        ],
        value='All',  # Default value
    ),

    html.Label('Select Date Range'),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=data['Date'].min(),
        end_date=data['Date'].max(),
        display_format='YYYY-MM-DD'
    ),

    dcc.Graph(id='sales-line-chart'),

    dcc.Graph(id='sales-bar-chart', figure=bar_fig),

    # Statistics section
    html.Div(id='stats-output')
])
# Callback to update the line chart and calculate statistics based on the selected category
@app.callback(
    [Output('sales-line-chart', 'figure'),
     Output('sales-bar-chart', 'figure'),
     Output('stats-output', 'children')],
    [Input('category-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('upload-data', 'contents')]
)
def update_chart(selected_category, start_date, end_date, contents):
    # Load data from uploaded file if available
    if contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        print("Uploaded Data Length:", len(data))
    else:
        # Default dataset
        data = pd.DataFrame({
            'Date': pd.date_range(start='1/1/2023', periods=10, freq='D'),
            'Sales': [100, 200, 150, 300, 250, 400, 350, 450, 500, 550],
            'Category': ['Electronics', 'Clothing', 'Electronics', 'Home', 'Electronics', 
                         'Clothing', 'Home', 'Clothing', 'Electronics', 'Home']
        })

    # Ensure Date column is in datetime format
    data['Date'] = pd.to_datetime(data['Date'])

    # Print the selected date range to the console
    print(f"Selected Date Range: {start_date} to {end_date}")

    # Filter data based on the selected category
    filtered_data = data

    if selected_category != 'All':
        filtered_data = filtered_data[filtered_data['Category'] == selected_category]

    # Further filter based on the selected date range
    filtered_data = filtered_data[(filtered_data['Date'] >= start_date) & (filtered_data['Date'] <= end_date)]

    # Print the filtered data to check if it's empty
    print("Filtered Data:")
    print(filtered_data)

    # Check if filtered data is empty
    if filtered_data.empty:
        return {}, {}, "No data available for the selected filters."

    # Create the figures as usual
    fig_line = px.line(filtered_data, x='Date', y='Sales', title=f'Sales Over Time - {selected_category}')
    fig_bar = px.bar(filtered_data.groupby('Category', as_index=False).sum(), 
                     x='Category', y='Sales', title='Total Sales by Category')

    # Calculate statistics
    total_sales = filtered_data['Sales'].sum()
    average_sales = filtered_data['Sales'].mean() if not filtered_data.empty else 0

    stats_text = f'Total Sales: {total_sales:.2f}Rs | Average Sales: {average_sales:.2f}Rs'
    return fig_line, fig_bar, stats_text

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)




