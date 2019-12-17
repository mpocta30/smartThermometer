import dash
import json
import plotly
import numpy
import pandas
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Output, Input
from datetime import datetime, timedelta
from tempDB import tempDB

# Defining the external stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        "https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css"]

# Initiliazing the dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Structuring the layout of the page
app.layout = html.Div([
    html.Div(className="navbar navbar-inverse bg-inverse", children=[
        html.A("Home Brew Temperature Monitor", className="navbar-brand", href="#")
    ]),
    html.Div(className="container", children=[
        dcc.Tabs(className="bottom-space", id="temp-tabs", value='current-temp', children=[
            dcc.Tab(label='Current Temp', value='current-temp'),
            dcc.Tab(label='Fahrenheit History', value='f-temp'),
            dcc.Tab(label='Celsius History', value='c-temp')
        ]),
        html.Div(className='text-center', children=[
            html.H3('Coming Soon...', id='current-temp-id'),
        ]),
        dcc.Dropdown(
            className="bottom-space",
            id='timerange_dropdown',
            options=[
                {'label': 'Show All', 'value': 'all'},
                {'label': 'Last Hour', 'value': 'onehour'},
                {'label': 'Last 12 Hours', 'value': 'twelvehours'},
                {'label': 'Last 24 Hours', 'value': 'day'}
            ],
            value='all'
        ),
        dcc.Graph(id='fahrenheit-scatter'),
        dcc.Graph(id='celsius-scatter'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,
            n_intervals=0
        ),
        html.Div(id='update-chart-data', style={'display': 'none'})
    ])
])



def findRecs(dropvalue):
    # Get the current datetime
    now = datetime.now()

    if dropvalue == 'all':
        return db.findAll()
    elif dropvalue == 'onehour':
        return db.find_byDate((now - timedelta(hours=1)))
    elif dropvalue == 'twelvehours':
        return db.find_byDate((now - timedelta(hours=12)))
    elif dropvalue == 'day':
        return db.find_byDate((now - timedelta(days=1)))



# Show/Hide the current temperature
@app.callback([Output('current-temp-id', 'style'),
               Output('fahrenheit-scatter', 'style'),
               Output('celsius-scatter', 'style'),
               Output('timerange_dropdown', 'style')],
              [Input('temp-tabs', 'value')])
def showhide_current(tab):
    current = {}
    fahr    = {} 
    cels    = {} 
    drop    = {}
    if tab == 'current-temp':
        current = {'display': 'block'}
        fahr    = {'display': 'none'}
        cels    = {'display': 'none'}
        drop    = {'display': 'none'}
    elif tab == 'f-temp':
        current = {'display': 'none'}
        fahr    = {'display': 'block'}
        cels    = {'display': 'none'}
        drop    = {'display': 'block'}
    elif tab == 'c-temp':
        current = {'display': 'none'}
        fahr    = {'display': 'none'}
        cels    = {'display': 'block'}
        drop    = {'display': 'block'}

    return current, fahr, cels, drop



# Read in new temp and get new chart values
@app.callback(Output('update-chart-data', 'children'),
              [Input('interval-component', 'n_intervals'),
              Input('timerange_dropdown', 'value')])
def update_chart_data(n, value):
    # Get brew temps
    global db
    mydatetime = datetime.now()
    twelveearlier = mydatetime - timedelta(hours=1)
    recs = findRecs(value)

    # Separate all elements
    ftemps = []
    ctemps = [] 
    times  = []
    for doc in recs:
        ftemps.append(doc['ftemp'])
        ctemps.append(doc['ctemp'])
        times.append(str(doc['time']))

    return json.dumps({'times': times, 'ftemps': ftemps, 'ctemps': ctemps})



@app.callback(Output('fahrenheit-scatter', 'figure'),
              [Input('update-chart-data', 'children')])
def update_fahr_scatter(children):
    dbvalues = json.loads(children)

    # Convert strings back to dates
    dates_list = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in dbvalues['times']]

    # Create the trace for temperature over time
    trace = plotly.graph_objs.Scatter(
                x=dates_list,
                y=dbvalues['ftemps'],
                name='Home Brew',
                mode='lines+markers'
            )

    # Figure to return
    fig = {
            'data': [trace],
            'layout': {
                'title': 'Temperature History in Fahrenheit',
                'xaxis': {'title': 'Date and Time'},
                'yaxis': {'title': 'Temperature '+ chr(176) + 'F'}
            }
        }

    return fig



@app.callback(Output('celsius-scatter', 'figure'),
              [Input('update-chart-data', 'children')])
def update_celsius_scatter(children):
    dbvalues = json.loads(children)

    # Convert strings back to dates
    dates_list = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in dbvalues['times']]

    # Create the trace for temperature over time
    trace = plotly.graph_objs.Scatter(
                x=dates_list,
                y=dbvalues['ctemps'],
                name='Home Brew',
                mode='lines+markers',
                marker=dict(
                    color='Orange'
                )
            )

    # Figure to return
    fig = {
            'data': [trace],
            'layout': {
                'title': 'Temperature History in Celsius',
                'xaxis': {'title': 'Date and Time'},
                'yaxis': {'title': 'Temperature '+ chr(176) + 'C'}
            }
        }

    return fig


if __name__ == '__main__':
    db = tempDB('mylib', 'temperatures')
    app.run_server(debug=True)