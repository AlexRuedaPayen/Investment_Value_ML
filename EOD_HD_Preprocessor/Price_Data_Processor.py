import requests
import pandas as pd

import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        #logging.FileHandler("debug.log"),
                        logging.StreamHandler()
                    ])
class Price_Data_Processor:
    def __init__(self, api_token):
        self.api_token = api_token

    def fetch_price_data(self, ticker_symbol, ticker_country, start_date):
        url = f'https://eodhd.com/api/eod/{ticker_symbol}.{ticker_country}?from={start_date}&period=d&api_token={self.api_token}&fmt=json'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_percentile_on_volume_weight(self, prices, total_volume, colname='close', percentile=10):

        values, weights = [price[colname] for price in prices], [price['volume'] for price in prices]
        combined_data = list(zip(values, weights))
        sorted_data = sorted(combined_data, key=lambda x: x[0])
        sorted_values, sorted_weights = zip(*sorted_data)

        tmpr = 0
        ind = 0


        for id, weight in enumerate(sorted_weights):
            tmpr += (weight / total_volume)
            if tmpr > (percentile / 100):
                break
            ind = id

        
        return float(sorted_values[ind])

    def process_prices(self, price_data, date_pairs):
        df = pd.DataFrame(index=[pd.to_datetime(pair[0]) for pair in date_pairs], columns=[
            'Equity___Low__close', 'Equity___Low__adjusted_close',
            'Equity___Median__close', 'Equity___Median__adjusted_close',
            'Equity___Total__Volume'
        ])


        for date_start, prices in date_pairs:
            if prices:
                if True:
                    total_volume = sum(price['volume'] for price in prices)
                    df.at[date_start, 'Equity___Low__close'] = self.get_percentile_on_volume_weight(prices, total_volume, 'close', 25)
                    df.at[date_start, 'Equity___Low__adjusted_close'] = self.get_percentile_on_volume_weight(prices, total_volume, 'adjusted_close', 25)
                    df.at[date_start, 'Equity___Median__close'] = self.get_percentile_on_volume_weight(prices, total_volume, 'close', 50)
                    df.at[date_start, 'Equity___Median__adjusted_close'] = self.get_percentile_on_volume_weight(prices, total_volume, 'adjusted_close', 50)
                    df.at[date_start, 'Equity___Total__Volume'] = int(total_volume)

                else:
                    logging.warning(f'Failure calculating price distribution for {date_start}')
            else:
                logging.warning(f'No data available for {date_start}')

        return df