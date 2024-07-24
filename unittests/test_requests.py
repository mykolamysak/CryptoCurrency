import unittest
from unittest.mock import patch, MagicMock
from main import MainWindow

class TestCryptoCurrencyApp(unittest.TestCase):

    @patch('main.requests.get')
    @patch('main.MainWindow.update_coin_list', return_value=None)  # mock
    def test_get_price(self, mock_update_coin_list, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'bitcoin': {'usd': 50000}}
        mock_get.return_value = mock_response

        app = MainWindow()
        app.current_currency = 'bitcoin'
        price = app.get_price()
        self.assertEqual(price, '50000')

    @patch('main.requests.get')
    def test_get_price_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        app = MainWindow()
        app.current_currency = 'non_existent_coin'
        price = app.get_price()
        self.assertEqual(price, 'N/A')

    @patch('main.requests.get')
    def test_update_price(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'bitcoin': {'usd': 50000}}
        mock_get.return_value = mock_response

        app = MainWindow()
        app.current_currency = 'bitcoin'
        app.update_price()
        self.assertEqual(app.current_price_label.cget('text'), '$50000')

    @patch('main.requests.get')
    def test_get_data_plot(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'prices': [[1622486400000, 40000], [1622572800000, 41000]],
            'total_volumes': [[1622486400000, 1000], [1622572800000, 1100]]
        }
        mock_get.return_value = mock_response

        app = MainWindow()
        app.current_currency = 'bitcoin'
        app.get_data_plot('1')

        self.assertEqual(app.highest_price, 41000)
        self.assertEqual(app.lowest_price, 40000)
        self.assertEqual(app.total_volume, 1100)

    @patch('main.requests.get')
    def test_get_coin_info(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'description': {'en': 'Bitcoin is a cryptocurrency.'},
            'links': {
                'twitter_screen_name': 'bitcoin',
                'facebook_username': 'bitcoin',
                'subreddit_url': 'https://reddit.com/r/bitcoin'
            }
        }
        mock_get.return_value = mock_response

        app = MainWindow()
        app.current_currency = 'bitcoin'
        coin_info = app.get_coin_info()
        self.assertEqual(coin_info['description'], 'Bitcoin is a cryptocurrency.')
        self.assertEqual(coin_info['twitter'], 'bitcoin')
        self.assertEqual(coin_info['facebook'], 'bitcoin')
        self.assertEqual(coin_info['reddit'], 'https://reddit.com/r/bitcoin')

if __name__ == '__main__':
    unittest.main()
