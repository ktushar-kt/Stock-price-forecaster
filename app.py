import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import yfinance as yf
import plotly.express as px
from model import prediction


def get_stock_price_fig(df):

    fig = px.line(df, x="Date", y=["Close", "Open"],
                  title="Closing and Openning Price vs Date")
    return fig


def get_more(df):
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    fig = px.scatter(df, x="Date", y="EMA_9",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig

# Creating a Dash instance and storing the application's server property
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.P("Welcome to the Stock price Forecaster App!", className="start"),
                html.Div(
                    [
                        html.P("Input stock code:"),
                        html.Div(
                            [
                                dcc.Input(id = 'dropdown_tickers', placeholder="Stock Code", type='text'),
                                html.Button('Submit', id = 'submit'),
                            ],
                            className='form')
                    ],
                    className='input'),
                html.Div(
                    [
                        dcc.DatePickerRange(id='date-picker-range',
                            min_date_allowed=dt(1995, 8, 5),
                            max_date_allowed=dt.now(),
                            initial_visible_month=dt.now(),
                            end_date=dt.now().date()),
                    ],
                    className='date'),
                html.Div(
                    [
                        html.Button('Stock Price', className="stock-btn", id="stock"),
                        html.Button('Indicators', className="indicators-btn", id="indicators"),
                        dcc.Input(id="n_days", type="text",placeholder="number of days"),
                        html.Button('Forecast', className="forecast-btn", id="forecast")
                    ],
                    className='buttons'),
            ],
            className="nav"),

        html.Div(
            [
                html.Div(
                    [
                        html.Img(id='logo'),
                        html.P(id='ticker')
                    ],
                    className="header"),
                html.Div(id="description", className="decription_ticker"),
                html.Div([], id="graphs-content"),
                html.Div([], id="main-content"),
                html.Div([], id="forecast-content")
            ],
            className="content")
    ],
    className="container")

# callback for company info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(n, val):
    if n == None:
        return "Hey there! Please enter a legitimate stock code to get details.", "", "", None, None, None
    else:
        if val == None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            inf = ticker.info
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df[['logo_url', 'shortName', 'longBusinessSummary']]
            return df['longBusinessSummary'].values[0], df['logo_url'].values[
                0], df['shortName'].values[0], None, None, None

@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]


@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]


@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)