import bfapi
import mock
import datetime
import unittest

def test_get_dates_times():
    today = bfapi.get_current_date()
    now = bfapi.get_current_time()
    assert datetime.datetime.strptime(today, '%Y-%m-%dT') is not ValueError
    assert datetime.datetime.strptime(now, '%H:%M:%S.%f') is not ValueError

def test_get_favourite():
    dicts = [{'marketId': 123, 'runners': [{'selectionId': 100, 'ex': {'availableToBack': [{'price': 5}, {'price': 2}]}}, {'selectionId': 200, 'ex': {'availableToBack': [{'price': 100}, {'price': 100}]}}]}]
    output = bfapi.get_favourite(dicts)
    assert output['price'] == 2
    assert output['selectionId'] == '100'

def test_get_event_time():
    market_catalogue = {'marketStartTime': '2018-08-30T10:00:00.000Z'}
    event_time = bfapi.get_event_time(market_catalogue)
    assert datetime.datetime.strptime(event_time, '%H:%M') is not ValueError

class Session(unittest.TestCase):
    @mock.patch('bfapi.requests.Session.post')
    def test_login(self, session_mock):
        token = {'token': 'abc'}
        session_mock.return_value = mock.MagicMock(json=mock.MagicMock(return_value=token))
        self.assertEqual(bfapi.login('usr', 'pw'), token['token'])

    @mock.patch('bfapi.requests.Session.post')
    def test_send_json_request(self, session_mock):
        token = {'result': 'success', 'token': 'abc'}
        session_mock.return_value = mock.MagicMock(json=mock.MagicMock(return_value=token))
        mock_login = bfapi.get_login_info('usr', 'pw')
        bf = bfapi.betfairexchange(mock_login)
        self.assertEqual(bf.send_json_request(''), token['result'])

    @mock.patch('bfapi.requests.Session.post')
    def test_order_favourite(self, session_mock):
        token = {'result': [{'marketId': 123, 'runners': [{'selectionId': 123, 'ex': {'availableToBack': [{'price': 5}, {'price': 1.1}]}}, {'selectionId': 000, 'ex': {'availableToBack': [{'price': 100}, {'price': 100}]}}]}], 'token': 'abc'}
        session_mock.return_value = mock.MagicMock(json=mock.MagicMock(return_value=token))
        mock_login = bfapi.get_login_info('usr', 'pw')
        bf = bfapi.betfairexchange(mock_login)
        output = bf.order_favourite('marketid')
        assert output == token['result']

    @mock.patch('bfapi.requests.Session.post')
    def tests_scheduled_bets(self, session_mock):
        token = {'token': 'abc'}
        session_mock.return_value = mock.MagicMock(json=mock.MagicMock(return_value=token))
        bf = bfapi.BetfairExchange('usr', 'pw')
        bf.schedule_orders('00:00', 'marketid')
        jobs = bfapi.schedule.jobs
        assert len(jobs) == 1
        bfapi.schedule.CancelJob
