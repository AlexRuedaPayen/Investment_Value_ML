import unittest
from unittest.mock import patch, MagicMock
from EOD_HD_Preprocessor.Price_Data_Processor import Price_Data_Processor
import pandas as pd

class TestPriceDataProcessorMock(unittest.TestCase):

    def setUp(self):
        self.processor = Price_Data_Processor(api_token='test_token')

    @patch('EOD_HD_Preprocessor.Price_Data_Processor.requests.get')
    def test_fetch_price_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'test_key': 'test_value'}
        mock_get.return_value = mock_response

        result = self.processor.fetch_price_data('AAPL', 'US', '2022-01-01')
        self.assertEqual(result, {'test_key': 'test_value'})
        mock_get.assert_called_once_with('https://eodhd.com/api/eod/AAPL.US?from=2022-01-01&period=d&api_token=test_token&fmt=json')

    def test_get_percentile_on_volume_weight(self):
        prices = [{'close': 100, 'volume': 10}, {'close': 200, 'volume': 20}, {'close': 300, 'volume': 30}]
        total_volume = 60
        result = self.processor.get_percentile_on_volume_weight(prices, total_volume, 'close', 50)
        self.assertEqual(result, 200)

    def test_process_prices(self):
        price_data = [
            ('2022-01-01', [{'close': 100,'adjusted_close': 100, 'volume': 10}, {'close': 200,'adjusted_close': 200, 'volume': 20}, {'close': 300,'adjusted_close': 300, 'volume': 30}]),
            ('2022-01-02', [{'close': 150,'adjusted_close': 100, 'volume': 15}, {'close': 250,'adjusted_close': 200, 'volume': 25}, {'close': 350, 'adjusted_close': 300,'volume': 35}])
        ]
        expected_df = pd.DataFrame({
            'Equity___Low__close': [100., 150.],
            'Equity___Low__adjusted_close': [100., 100.],
            'Equity___Median__close': [200., 150.],
            'Equity___Median__adjusted_close': [200., 100.],
            'Equity___Total__Volume': [60., 75.]
        }, index=pd.to_datetime(['2022-01-01', '2022-01-02']))

        result_df = self.processor.process_prices(price_data, [('2022-01-01', price_data[0][1]), ('2022-01-02', price_data[1][1])])


        pd.testing.assert_frame_equal(result_df, expected_df)

if __name__ == '__main__':
    unittest.main()