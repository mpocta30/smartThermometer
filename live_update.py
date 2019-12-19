import dash
import json
import plotly
import numpy
import pandas
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Output, Input, State
from datetime import datetime, timedelta
from tempDB import tempDB
from twilio_sms import Twilio
from ds18b20 import thermSensor

# Global variables
degree = chr(176)

# Defining the external stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        "https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css"]

# Initiliazing the dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Structuring the layout of the page
app.layout = html.Div([
    dcc.ConfirmDialog(
        id='start-confirm',
        message='Are you sure you want to START recording the temperature?'
    ),
    dcc.ConfirmDialog(
        id='stop-confirm',
        message='Are you sure you want to STOP recording the temperature?'
    ),
    dcc.ConfirmDialog(
        id='cleardb-confirm',
        message='Are you sure you want to remove all data from the database?'
    ),
    html.Div(className="navbar navbar-inverse bg-inverse", children=[
        html.A("Home Brew Temperature Monitor", className="navbar-brand", href="#"),
        html.Ul(className="nav navbar-nav navbar-right", children=[
            html.Button("Stop", 
                    id="stop-toggle", 
                    type="button", 
                    className="btn btn-danger navbar-btn",
                    style={"margin-right": "20px",
                           "display": "none"}
                ),
            html.Button("Start", 
                    id="start-toggle", 
                    type="button", 
                    className="btn btn-success navbar-btn",
                    style={"margin-right": "20px",
                           "display": "block"}
                )  
        ])
    ]),
    html.Div(className="container", children=[
        dcc.Tabs(className="bottom-space", id="temp-tabs", value='current-temp', children=[
            dcc.Tab(label='Current Temp', value='current-temp'),
            dcc.Tab(label='Fahrenheit History', value='f-temp'),
            dcc.Tab(label='Celsius History', value='c-temp')
        ]),
        html.P(id="output"),
        html.Div(id='alert-control', children=[
            html.Div(id='current-temp-id', className='text-center bottom-space', children=[]),
            html.Div(className="col-sm-6", children=[
                dcc.Markdown('''
                    Use the switch below to turn alerts `On/Off`
                '''),
                daq.BooleanSwitch(
                    id='alert-toggle',
                    on=False,
                    color="#5cb85c"
                ),
                dcc.Markdown('''
                    Use this button to clear the current temperature data from
                    the database.''',
                    style={'margin-top': '20px'}
                ),
                html.Button("Clear Database", 
                    id="clearDB", 
                    type="button", 
                    className="btn btn-danger"
                )  
            ]),
            html.Div(className="col-sm-6", children=[
                dcc.Markdown('''
                    Choose whether you would like to trigger an alert in `Celsius`
                    or `Fahrenheit`.  Then enter the temperature you would like to
                    use as the threshold.
                '''),
                dcc.Dropdown(
                    className="bottom-space",
                    id='cf_dropdown',
                    options=[
                        {'label': 'Fahrenheit', 'value': 'fahr'},
                        {'label': 'Celsius', 'value': 'cels'}
                    ],
                    value='fahr',
                    clearable=False
                ),
                daq.NumericInput(
                    id='alert-threshold',
                    min=0,
                    max=300,
                    value=0,
                    size=200
                )
            ]),
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
            value='all',
            clearable=False
        ),
        dcc.Graph(id='fahrenheit-scatter'),
        dcc.Graph(id='celsius-scatter'),
        dcc.Interval(
            id='interval-component',
            interval=5*1000,
            n_intervals=0,
            disabled=True
        ),
        html.Div(id='update-chart-data', style={'display': 'none'})
    ])
])



# Find the recs based on time selected
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



# Confirm start/stop recording data
@app.callback([Output('interval-component', 'disabled'),
                Output('start-toggle', 'style'),
                Output('stop-toggle', 'style')],
                [Input('start-confirm', 'submit_n_clicks'),
                Input('stop-confirm', 'submit_n_clicks')])
def toggle_interval(start_clicks, stop_clicks):
    start = {}
    stop  = {}
    trigger = dash.callback_context.triggered[0]

    if trigger['value']:
        if trigger['prop_id'] == 'stop-confirm.submit_n_clicks':
            start = {'display': 'block',
                    'margin-right': '20px'}
            stop  = {'display': 'none',
                    'margin-right': '20px'}
            return True, start, stop
        else:
            start = {'display': 'none',
                    'margin-right': '20px'}
            stop  = {'display': 'block',
                    'margin-right': '20px'}
            return False, start, stop
    else:
        start = {'display': 'block',
                'margin-right': '20px'}
        stop  = {'display': 'none',
                'margin-right': '20px'}
        return True, start, stop



# Start/Stop recording temperature data
@app.callback([Output('stop-confirm', 'displayed'),
                Output('start-confirm', 'displayed')],
                [Input('start-toggle', 'n_clicks'),
                Input('stop-toggle', 'n_clicks')])
def open_startstop_dialogues(start_clicks, stop_clicks):
    start = {}
    stop  = {}
    trigger = dash.callback_context.triggered[0]

    if trigger['value']:
        if trigger['prop_id'] == 'stop-toggle.n_clicks':
            return True, False
        else:
            return False, True
    else:
        return False, False



# Clear all temperature data
@app.callback(Output('cleardb-confirm', 'displayed'),
                [Input('clearDB', 'n_clicks')])
def open_cleardialog(clear_clicks):
    trigger = dash.callback_context.triggered[0]

    if trigger['value']:
        return True
    return False



# Confirm clear collection
@app.callback(Output('clearDB', 'disabled'),
            [Input('cleardb-confirm', 'submit_n_clicks'),
            Input('update-chart-data', 'children')])
def clearDB(clear_clicks, children):
    trigger = dash.callback_context.triggered[0]

    if trigger['value']:
        if trigger['prop_id'] == 'cleardb-confirm.submit_n_clicks':
            db.clearCollection()
            return True
        else:
            return False
    else:
        return False



# Show/Hide the current temperature
@app.callback([Output('alert-control', 'style'),
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
@app.callback([Output('update-chart-data', 'children'),
              Output('current-temp-id', 'children')],
              [Input('interval-component', 'n_intervals'),
              Input('timerange_dropdown', 'value')],
              [State('alert-toggle', 'on'),
              State('alert-threshold', 'value'),
              State('cf_dropdown', 'value')])
def update_chart_data(n, value, toggle, threshold, unit):
    # Get current temps
    newC, newF = temp.getTemp()

    # Display new temp values
    newTemps = html.H3('The temperature is currently ' + str(newF) + degree \
                + 'F and ' + str(newC) + degree + 'C')

    # Current datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')

    # Insert the new temps
    db.insertTemps(now, newC, newF)

    # If alerts are enabled check temp and send alert
    # if current temp is >= to the threshold
    if toggle and not threshold is None:
        if unit == 'fahr' and newF >= threshold:
            print("Alert fahrenheit!")
        elif unit == 'cels' and newC >= threshold:
            print("Alert celsius!")

    # Get brew historical temps
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

    tempData = json.dumps({'times': times, 'ftemps': ftemps, 'ctemps': ctemps})

    return tempData, newTemps



# Create Fahrenheit Scatter Plot
@app.callback(Output('fahrenheit-scatter', 'figure'),
              [Input('update-chart-data', 'children')])
def update_fahr_scatter(children):
    trigger = dash.callback_context.triggered[0]

    if trigger['value']:
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
                    'yaxis': {'title': 'Temperature '+ degree + 'F'}
                }
            }

        return fig
    else:
        # Figure to return
        fig = {
                'layout': {
                    'title': 'Temperature History in Fahrenheit',
                    'xaxis': {'title': 'Date and Time'},
                    'yaxis': {'title': 'Temperature '+ degree + 'F'}
                }
            }

        return fig



# Create Celsius Scatter Plot
@app.callback(Output('celsius-scatter', 'figure'),
              [Input('update-chart-data', 'children')])
def update_celsius_scatter(children):
    trigger = dash.callback_context.triggered[0]

    if trigger['value']:
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
                    'yaxis': {'title': 'Temperature '+ degree + 'C'}
                }
            }

        return fig
    else:
        # Figure to return
        fig = {
                'layout': {
                    'title': 'Temperature History in Celsius',
                    'xaxis': {'title': 'Date and Time'},
                    'yaxis': {'title': 'Temperature '+ degree + 'C'}
                }
            }

        return fig


if __name__ == '__main__':
    db   = tempDB('mylib', 'temperatures')
    sms  = Twilio()
    temp = thermSensor()
    app.run_server(debug=True)