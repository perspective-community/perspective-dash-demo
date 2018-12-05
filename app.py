# -*- coding: utf-8 -*-
import os
import flask
import functools
import dash
import pyEX as p
import json
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from perspective_dash_component import perspective_dash

# Default data
symbols = p.symbols()
default_data = p.chartDF('JPM', '6m').to_dict(orient='records')

# dash
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

app.layout = html.Div(children=[
    html.H1(children='Perspective Demo', style={'textAlign': 'center'}),
    dcc.Dropdown(id='tickerinput', value='JPM', options=[{'label': s['symbol'] + ' - ' + s['name'], 'value': s['symbol']} for s in symbols]),
    perspective_dash(id='psp1', value=default_data, view='y_line', columns=['open', 'high', 'low', 'close']),
    perspective_dash(id='psp2', value=default_data),
    html.Div(id='intermediate-value', style={'display': 'none'})
    ],
    style={'height': '100%',
           'width': '100%',
           'display': 'flex',
           'flex-direction': 'column'})


@functools.lru_cache(100)
def fetch_data(value):
    return p.chartDF(value, '6m')


@app.callback(Output('intermediate-value', 'children'), [Input('tickerinput', 'value')])
def fetch_new_data(value):
    return fetch_data(value).to_json(orient='records')


@app.callback(Output('psp1', 'value'), [Input('intermediate-value', 'children')])
def update_psp1(value):
    return json.loads(value)


@app.callback(Output('psp2', 'value'), [Input('intermediate-value', 'children')])
def update_psp2(value):
    return json.loads(value)

if __name__ == "__main__":
    port = os.environ.get('PORT')
    # heroku
    if port: app.run_server(port=port, debug=False, threaded=True)
    else: app.run_server(debug=True, threaded=True)
