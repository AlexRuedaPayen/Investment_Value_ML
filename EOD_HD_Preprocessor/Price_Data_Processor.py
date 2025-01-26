import requests
import pandas as pd


class Price_Data_Processor:
    def __init__(self, api_token):
        self.api_token = api_token

    def fetch_price_data(self, ticker_symbol, ticker_country, start_date):
        url = f'https://eodhd.com/api/eod/{ticker_symbol}.{ticker_country}?from={start_date}&period=d&api_token={self.api_token}&fmt=json'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def process_prices(self, price_data, date_pairs):
        # Similar to the logic you had for processing prices
        pass
