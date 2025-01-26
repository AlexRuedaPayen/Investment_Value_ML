import datetime
from EOD_HD_Preprocessor.Financial_Processor import Financial_Processor
from EOD_HD_Preprocessor.Price_Data_Processor import Price_Data_Processor

from data.Financials import assets,liabilities,equity,revenue_and_costs

class CompanyDataManager:
    def __init__(self, api_token):
        self.financial_processor = Financial_Processor(api_token)
        self.price_processor = Price_Data_Processor(api_token)

    def process_company_data(self, ticker_name, ticker_symbol, ticker_country):
        # 1. Fetch and process financial data
        financial_data = self.financial_processor.fetch_financial_data(ticker_symbol, ticker_country)
        dates = sorted(financial_data['Financials']['Balance_Sheet']['quarterly'].keys())
        df_financials = self.financial_processor.process_financials(financial_data, dates, assets, liabilities, equity, revenue_and_costs)

        # 2. Fetch and process price data
        price_data = self.price_processor.fetch_price_data(ticker_symbol, ticker_country, min(dates))
        # Process prices and merge with financial data
        pass

        # 3. Save or upload the data
        pass
