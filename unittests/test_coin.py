import unittest
from unittest.mock import patch, MagicMock
from main import MainWindow
import customtkinter as ctk


class TestCryptoCurrencyAppAdditional(unittest.TestCase):

    @patch('main.MainWindow.init_main', return_value=None)
    @patch('main.MainWindow.update_global_market_info', return_value=None)
    @patch('main.MainWindow.update_coin_list', return_value=None)
    @patch('main.MainWindow.update_price', return_value=None)
    @patch('main.MainWindow.update_social_links', return_value=None)
    @patch('main.MainWindow.update_brief_description', return_value=None)
    @patch('main.MainWindow.get_data_and_plot', return_value=None)
    def setUp(self, *args):
        with patch.object(MainWindow, '__init__', return_value=None):
            self.app = MainWindow()

        # Mock necessary attributes
        self.app.current_currency = 'bitcoin'
        self.app.global_market_info_label = MagicMock()
        self.app.global_market_cap_label = MagicMock()
        self.app.current_price_label = MagicMock()
        self.app.social_frame = MagicMock()
        self.app.high_low_frame = MagicMock()
        self.app.theme_switcher = MagicMock()
        self.app.high_low_title = MagicMock()
        self.app.time_span_segmented_button = MagicMock()

        # Mock icons
        self.app.x_icon = MagicMock()
        self.app.fb_icon = MagicMock()
        self.app.reddit_icon = MagicMock()
        self.app.twitter_icon = MagicMock()
        self.app.facebook_icon = MagicMock()

        # Mock cget method
        self.app.cget = MagicMock(return_value="#000000")  # or any other color

    @patch('main.requests.get')
    def test_get_price(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'bitcoin': {'usd': 50000}}
        mock_get.return_value = mock_response

        price = self.app.get_price()
        self.assertEqual(price, '50000')

    @patch('main.requests.get')
    def test_update_global_market_info(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {
                'total_volume': {'usd': 1000000000},
                'total_market_cap': {'usd': 2000000000000}
            }
        }
        mock_get.return_value = mock_response

        self.app.update_global_market_info()
        self.app.global_market_info_label.configure.assert_called_with(text='Total market volume: $1,000,000,000.00')
        self.app.global_market_cap_label.configure.assert_called_with(text='Global market cap: $2,000,000,000,000.00')

    @patch('main.requests.get')
    @patch('customtkinter.CTkButton')
    def test_update_social_links(self, mock_button, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'links': {
                'twitter_screen_name': 'test_twitter',
                'facebook_username': 'test_facebook',
                'subreddit_url': 'https://reddit.com/r/test'
            }
        }
        mock_get.return_value = mock_response

        self.app.current_currency = 'test_coin'
        self.app.update_social_links()

        # Check if CTkButton was called 3 times (for Twitter, Facebook, and Reddit)
        self.assertEqual(mock_button.call_count, 3)

        # You can add more assertions here to check the exact calls to CTkButton if needed


if __name__ == '__main__':
    unittest.main()