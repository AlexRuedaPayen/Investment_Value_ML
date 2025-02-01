import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from EOD_HD_Preprocessor.Company_Data_Manager import CompanyDataManager
from EOD_HD_Preprocessor.Financial_Processor import FinancialDataProcessor
from EOD_HD_Preprocessor.Price_Data_Processor import Price_Data_Processor

class TestCompanyDataManager(unittest.TestCase):

    def setUp(self):
        self.api_token = 'test_token'
        self.manager = CompanyDataManager(self.api_token)

    @patch.object(FinancialDataProcessor, 'fetch_financial_data')
    @patch.object(FinancialDataProcessor, 'process_financials')
    @patch.object(Price_Data_Processor, 'fetch_price_data')
    @patch.object(Price_Data_Processor, 'process_prices')
    #@patch('CompanyDataManager.save_data')

    def test_process_company_data(self, mock_save_data, mock_process_prices, mock_fetch_price_data, mock_process_financials, mock_fetch_financial_data):
        # Mocking the fetched data
        mock_financial_data = {
            'Financials': {
                'Balance_Sheet': {
                    'quarterly': {
                        '2021-01-01': {},
                        '2021-04-01': {}
                    }
                }
            }
        }
        mock_fetch_financial_data.return_value = mock_financial_data
        mock_process_financials.return_value = pd.DataFrame({
            'Balance_Sheet___asset1': [100, 200],
            'Balance_Sheet___asset2': [300, 400]
        }, index=pd.to_datetime(['2021-01-01', '2021-04-01']))

        # Mocking the price data

        import pdb
        pdb.set_trace()
        mock_price_data = [
            {'close': 100, 'adjusted_close': 100, 'volume': 10},
            {'close': 200, 'adjusted_close': 200, 'volume': 20}
        ]
        mock_fetch_price_data.return_value = mock_price_data
        mock_process_prices.return_value = pd.DataFrame({
            'Equity___Low__close': [100, 150],
            'Equity___Low__adjusted_close': [100, 150],
            'Equity___Median__close': [200, 150],
            'Equity___Median__adjusted_close': [200, 100],
            'Equity___Total__Volume': [60, 75]
        }, index=pd.to_datetime(['2021-01-01', '2021-04-01']))

        # Call the method to test
        self.manager.process_company_data('TestCompany', 'TEST', 'US')

        # Assert that save_data was called
        self.assertTrue(mock_save_data.called)

    def test_merge_financials_and_prices(self):
        df_financials = pd.DataFrame({
            'Balance_Sheet___asset1': [100., 200.],
            'Balance_Sheet___asset2': [300., 400.]
        }, index=pd.to_datetime(['2021-01-01', '2021-04-01']))
        df_prices = pd.DataFrame({
            'Equity___Low__close': [100., 150.],
            'Equity___Low__adjusted_close': [100., 150.],
            'Equity___Median__close': [200., 150.],
            'Equity___Median__adjusted_close': [200., 100.],
            'Equity___Total__Volume': [60., 75.]
        }, index=pd.to_datetime(['2021-01-01', '2021-04-01']))

        merged_df = self.manager.merge_financials_and_prices(df_financials, df_prices)

        expected_df = pd.DataFrame({
            'Balance_Sheet___asset1': [100., 200.],
            'Balance_Sheet___asset2': [300., 400.],
            'Equity___Low__close': [100., 150.],
            'Equity___Low__adjusted_close': [100., 150.],
            'Equity___Median__close': [200., 150.],
            'Equity___Median__adjusted_close': [200., 100.],
            'Equity___Total__Volume': [60., 75.]
        }, index=pd.to_datetime(['2021-01-01', '2021-04-01']))


        pd.testing.assert_frame_equal(merged_df, expected_df)

if __name__ == '__main__':
    unittest.main()