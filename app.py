# -*- coding: utf-8 -*-
import os
import flask
import functools
import dash
import pyEX as p
import pyEXstudies as ps
import json
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from perspective_dash_component import PerspectiveDash


################################
# Helpers to cache data lookup #
@functools.lru_cache(100)
def fetch_data(value):
    return p.chartDF(value, '6m').to_dict(orient='records')


@functools.lru_cache(100)
def fetch_corr_data(value):
    df = ps.peerCorrelation(value)
    df.index.name = 'symbols'
    return df.index.tolist(), df.reset_index().to_dict(orient='records')
################################

################
# Default data #
symbols = p.symbols()
default_data = fetch_data('JPM')
default_data2 = fetch_corr_data('JPM')
default_data2cols, default_data2data = default_data2
################

################
# dash
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
################

################
# layout
app.layout = html.Div(children=[
    html.H1(children='Perspective Demo', style={'textAlign': 'center'}),
    dcc.Dropdown(id='tickerinput', value='JPM', options=[{'label': s['symbol'] + ' - ' + s['name'], 'value': s['symbol']} for s in symbols]),
    PerspectiveDash(id='psp1', data=default_data, view='y_line', columns=['open', 'high', 'low', 'close']),
    html.Div(children=[
                        PerspectiveDash(id='psp2', data=default_data),
                        PerspectiveDash(id='psp3', data=default_data2data, view='heatmap', columns=default_data2cols, rowpivots=['symbols'])],
             style={'width': '100%', 'display': 'flex', 'flex-direction': 'row'}),
    html.Div(id='intermediate-value', style={'display': 'none'})
    ],
    style={'height': '100%', 'width': '100%', 'display': 'flex', 'flex-direction': 'column'})
################


################
# callbacks
@app.callback(Output('intermediate-value', 'children'), [Input('tickerinput', 'value')])
def fetch_new_data(value):
    return json.dumps(fetch_data(value))


@app.callback(Output('psp1', 'data'), [Input('intermediate-value', 'children')])
def update_psp1(value):
    return json.loads(value)


@app.callback(Output('psp2', 'data'), [Input('intermediate-value', 'children')])
def update_psp2(value):
    return json.loads(value)


# Data
@app.callback(Output('psp3', 'data'), [Input('tickerinput', 'value')])
def update_psp3data(value):
    return fetch_corr_data(value)[1]


# Columns
@app.callback(Output('psp3', 'columns'), [Input('tickerinput', 'value')])
def update_psp3cols(value):
    return fetch_corr_data(value)[0]
################

################
# Run
if __name__ == "__main__":
    port = os.environ.get('PORT')
    # heroku
    if port: app.run_server(port=port, debug=False, threaded=True)
    else: app.run_server(debug=True, threaded=True)
