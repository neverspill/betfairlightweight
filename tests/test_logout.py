import unittest
import mock
from requests.exceptions import ConnectionError

from tests.tools import create_mock_json
from betfairlightweight.endpoints.logout import Logout
from betfairlightweight import APIClient
from betfairlightweight.exceptions import LogoutError, APIError


class LogoutTest(unittest.TestCase):

    def setUp(self):
        client = APIClient('username', 'password', 'app_key', 'UK')
        self.logout = Logout(client)

    @mock.patch('betfairlightweight.endpoints.logout.Logout.request')
    def test_call(self, mock_response):
        mock = create_mock_json('tests/resources/logout_success.json')
        mock_response.return_value = mock
        response = self.logout()

        assert response == mock.json()
        assert self.logout.client.session_token is None

    @mock.patch('betfairlightweight.baseclient.BaseClient.cert')
    @mock.patch('betfairlightweight.baseclient.BaseClient.keep_alive_headers')
    @mock.patch('betfairlightweight.baseclient.requests.post')
    def test_request(self, mock_post, mock_logout_headers, mock_cert):
        mock_response = create_mock_json('tests/resources/logout_success.json')
        mock_post.return_value = mock_response

        mock_headers = mock.Mock()
        mock_headers.return_value = {}
        mock_logout_headers.return_value = mock_headers

        mock_client_cert = mock.Mock()
        mock_client_cert.return_value = []
        mock_cert.return_value = mock_client_cert

        url = 'https://identitysso.betfair.com/api/logout'
        response = self.logout.request()

        mock_post.assert_called_once_with(url, headers=mock_logout_headers, cert=mock_cert)
        assert response == mock_response

    @mock.patch('betfairlightweight.baseclient.BaseClient.cert')
    @mock.patch('betfairlightweight.baseclient.BaseClient.keep_alive_headers')
    @mock.patch('betfairlightweight.baseclient.requests.post')
    def test_request_error(self, mock_post, mock_logout_headers, mock_cert):
        mock_post.side_effect = ConnectionError()
        mock_headers = mock.Mock()
        mock_headers.return_value = {}
        mock_logout_headers.return_value = mock_headers

        mock_client_cert = mock.Mock()
        mock_client_cert.return_value = []
        mock_cert.return_value = mock_client_cert

        url = 'https://identitysso.betfair.com/api/logout'
        with self.assertRaises(APIError):
            self.logout.request()

        mock_post.assert_called_once_with(url, headers=mock_logout_headers, cert=mock_cert)

    @mock.patch('betfairlightweight.baseclient.BaseClient.cert')
    @mock.patch('betfairlightweight.baseclient.BaseClient.keep_alive_headers')
    @mock.patch('betfairlightweight.baseclient.requests.post')
    def test_request_error_random(self, mock_post, mock_logout_headers, mock_cert):
        mock_post.side_effect = ValueError()
        mock_headers = mock.Mock()
        mock_headers.return_value = {}
        mock_logout_headers.return_value = mock_headers

        mock_client_cert = mock.Mock()
        mock_client_cert.return_value = []
        mock_cert.return_value = mock_client_cert

        url = 'https://identitysso.betfair.com/api/logout'
        with self.assertRaises(APIError):
            self.logout.request()

        mock_post.assert_called_once_with(url, headers=mock_logout_headers, cert=mock_cert)

    def test_logout_error_handler(self):
        mock_response = create_mock_json('tests/resources/logout_success.json')
        assert self.logout._error_handler(mock_response.json()) is None

        mock_response = create_mock_json('tests/resources/logout_fail.json')
        with self.assertRaises(LogoutError):
            self.logout._error_handler(mock_response.json())

    def test_url(self):
        assert self.logout.url == 'https://identitysso.betfair.com/api/logout'
