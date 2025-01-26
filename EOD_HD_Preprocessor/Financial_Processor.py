import requests
import pandas as pd

import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        #logging.FileHandler("debug.log"),
                        logging.StreamHandler()
                    ])
class FinancialDataProcessor:
    def __init__(self, api_token):
        self.api_token = api_token

    def fetch_financial_data(self, ticker_symbol, ticker_country):
        url = f'https://eodhd.com/api/fundamentals/{ticker_symbol}.{ticker_country}?api_token={self.api_token}&fmt=json'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def create_columns(self, categories, data_type):
        return [f'{data_type}___{col}' for col in categories]

    def process_balance_sheet(self, df, data, date, col_name):
        try:
            value = data['Financials']['Balance_Sheet']['quarterly'][date].get(col_name)
            if value:
                df.at[date, f'Balance_Sheet___{col_name}'] = float(value)
        except KeyError:
            pass

    def process_income_statement(self, df, data, date, col_name):
        try:
            value = data['Financials']['Income_Statement']['quarterly'][date].get(col_name)
            if value:
                df.at[date, f'Income_Statement___{col_name}'] = float(value)
        except KeyError:
            pass

    def process_financials(self, data, dates, assets, liabilities, equity, income_statement_categories):
        columns = (
            self.create_columns(assets, 'Balance_Sheet') +
            self.create_columns(liabilities, 'Balance_Sheet') +
            self.create_columns(equity, 'Balance_Sheet') +
            self.create_columns(income_statement_categories, 'Income_Statement')
        )

        df = pd.DataFrame(index=pd.to_datetime(dates), columns=columns).sort_index()

        for date in dates:
            for col in columns:
                if col.startswith('Balance_Sheet'):
                    self.process_balance_sheet(df, data, date, col.split('___')[1])
                elif col.startswith('Income_Statement'):
                    self.process_income_statement(df, data, date, col.split('___')[1])

        return df