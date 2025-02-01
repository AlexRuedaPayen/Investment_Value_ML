import os
import datetime
import pandas as pd
from EOD_HD_Preprocessor.Financial_Processor import FinancialDataProcessor
from EOD_HD_Preprocessor.Price_Data_Processor import Price_Data_Processor

from data.Financials import assets, liabilities, equity, revenue_and_costs, operating_income_and_expenses, interest_and_taxes, net_income_components

import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        #logging.FileHandler("debug.log"),
                        logging.StreamHandler()
                    ])

class CompanyDataManager:
    def __init__(self, api_token):
        self.financial_processor = FinancialDataProcessor(api_token)
        self.price_processor = Price_Data_Processor(api_token)

    def process_company_data(self, ticker_name, ticker_symbol, ticker_country):
        # 1. Fetch and process financial data
        financial_data = self.financial_processor.fetch_financial_data(ticker_symbol, ticker_country)
        dates = sorted(financial_data['Financials']['Balance_Sheet']['quarterly'].keys())
        df_financials = self.financial_processor.process_financials(
            financial_data, dates, assets, liabilities, equity,
            revenue_and_costs + operating_income_and_expenses + interest_and_taxes + net_income_components
        )

        # 2. Fetch and process price data
        min_date = min(dates)
        price_data = self.price_processor.fetch_price_data(ticker_symbol, ticker_country, min_date)
        date_pairs = list(zip(pd.to_datetime(dates[1:]), pd.to_datetime(dates[:-1])))
        df_prices = self.price_processor.process_prices(price_data, date_pairs)

        # Merge financials and price data
        merged_df = self.merge_financials_and_prices(df_financials, df_prices)

        # 3. Save or upload the data
        self.save_data(merged_df, ticker_name, ticker_symbol)

    def merge_financials_and_prices(self, df_financials, df_prices):
        df_financials.index = pd.to_datetime(df_financials.index)
        df_prices.index = pd.to_datetime(df_prices.index)
        merged_df = pd.merge(df_financials, df_prices, left_index=True, right_index=True, how='inner')
        merged_df.index = pd.to_datetime(merged_df.index)  
        return merged_df

    def save_data(self, df, ticker_name, ticker_symbol):
        symbol_name_contraction = f'{ticker_symbol}___{ticker_name}'.replace('/', ';')
        path_folder = f'./data/Companies/{symbol_name_contraction}/'
        path_file = f'{path_folder}{symbol_name_contraction}___V4.xlsx'
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)

        df.to_excel(path_file)
        # upload_file(service, path_file, folder_id=get_folder_id(country_code=country_name, exchange_code=ticker_country))
        # remove_folder(path_folder)
        logging.info(f'Success uploading data to Google Drive for company {ticker_name}')