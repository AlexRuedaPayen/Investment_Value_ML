import unittest
from unittest.mock import patch, MagicMock
from EOD_HD_Preprocessor.Financial_Processor import FinancialDataProcessor
import pandas as pd

class TestFinancialDataProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = FinancialDataProcessor(api_token='test_token')

    @patch('EOD_HD_Preprocessor.Financial_Processor.requests.get')
    def test_fetch_financial_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'test_key': 'test_value'}
        mock_get.return_value = mock_response

        result = self.processor.fetch_financial_data('AAPL', 'US')
        self.assertEqual(result, {'test_key': 'test_value'})
        mock_get.assert_called_once_with('https://eodhd.com/api/fundamentals/AAPL.US?api_token=test_token&fmt=json')

    def test_create_columns(self):
        categories = ['asset1', 'asset2']
        result = self.processor.create_columns(categories, 'Balance_Sheet')
        self.assertEqual(result, ['Balance_Sheet___asset1', 'Balance_Sheet___asset2'])

    def test_process_balance_sheet(self):
        df = pd.DataFrame(columns=['Balance_Sheet___asset1'])
        data = {'Financials': {'Balance_Sheet': {'quarterly': {'2021-01-01': {'asset1': 100}}}}}
        self.processor.process_balance_sheet(df, data, '2021-01-01', 'asset1')
        self.assertEqual(df.at['2021-01-01', 'Balance_Sheet___asset1'], 100.0)

    def test_process_income_statement(self):
        df = pd.DataFrame(columns=['Income_Statement___income1'])
        data = {'Financials': {'Income_Statement': {'quarterly': {'2021-01-01': {'income1': 200}}}}}
        self.processor.process_income_statement(df, data, '2021-01-01', 'income1')
        self.assertEqual(df.at['2021-01-01', 'Income_Statement___income1'], 200.0)

    def test_process_financials(self):
        data = {
            'Financials': {
                'Balance_Sheet': {'quarterly': {'2021-01-01': {'asset1': 100}}},
                'Income_Statement': {'quarterly': {'2021-01-01': {'income1': 200}}}
            }
        }
        dates = ['2021-01-01']
        assets = ['asset1']
        liabilities = []
        equity = []
        income_statement_categories = ['income1']
        
        result_df = self.processor.process_financials(data, dates, assets, liabilities, equity, income_statement_categories)
        self.assertEqual(result_df.at['2021-01-01', 'Balance_Sheet___asset1'], 100.0)
        self.assertEqual(result_df.at['2021-01-01', 'Income_Statement___income1'], 200.0)

if __name__ == '__main__':
    unittest.main()