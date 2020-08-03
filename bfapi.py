import time
import ssl
import datetime
import schedule
import logging
import parameters  # functions returning json parameters
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

logging.getLogger('schedule').propagate = False

REQ_PREFIX = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/'

#api uses UTC time, 1 hour behind UK summer time
class BetfairExchange(object):
    def __init__(self, login_info):
        self.login_info = login_info
        self.token = login(self.login_info)
        self.header = {
            'X-Application': parameters.app_key,
            'X-Authentication': self.token,
            'content-type': 'application/json'
        }
        self.url = "https://api.betfair.com/exchange/betting/json-rpc/v1"

    def send_json_request(self, json_request):
        logger = create_logger()
        logger.info({'data': json_request, 'headers': self.header, 'time': get_current_time()})
        json_request = json_request.encode('utf-8')
        session = requests.Session()
        req = session.post(url=self.url, data=json_request, headers=self.header)
        req = req.json()
        logger.info({'result': req['result'], 'time': get_current_time()})
        return req['result']

    def list_market_catalogue(self):
        json = parameters.list_market_catalogue_json()
        result = self.send_json_request(json)
        return result

    def list_market_book(self, market_id):
        json = parameters.list_market_book_json(market_id) 
        result = self.send_json_request(json)
        return result

    def list_cleared_orders(self, date):
        json = parameters.list_cleared_orders_json(date)
        results = self.send_json_request(json)
        return results['clearedOrders']

    def order_favourite(self, market_id):
        mb_json = parameters.list_market_book_json(market_id)
        market_book = self.send_json_request(mb_json)
        runner = get_favourite(market_book)
        json = parameters.place_orders_json(runner['marketId'], runner['selectionId'], runner['price'])
        order = self.send_json_request(json)
        return order 

    def schedule_orders(self, event_time, market_id):
        schedule.every().day.at(event_time).do(self.order_favourite, market_id)

def login(login_info):
    header = {
        'Accept': 'application/json',
        'X-Application': parameters.app_key,
    }
    session = requests.Session()
    response = session.post(url='https://identitysso.betfair.com/api/login', headers=header, data=login_info, verify=False)
    print(response.json())
    return response.json()['token'] 

def get_login_info(username, password):
    data = [
        ('username', username),
        ('password', password),
    ]
    return data

def create_logger():
    date_name = get_current_date()
    name = 'logs/{}.log'.format(date_name)
    logging.basicConfig(filename=name, level=logging.DEBUG)
    logger = logging.getLogger()
    return logger

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def get_event_time(market_catalogue):
    event_time = market_catalogue['marketStartTime']
    event_time = datetime.datetime.strptime(event_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    event_time = datetime.datetime.strftime(event_time, '%H:%M')
    return event_time

def get_favourite(market_book):
    runners = market_book[0]['runners']
    price_list = []
    for runner in runners:
        prices = runner['ex']['availableToBack']
        for price in prices:
            price.update({'selectionId': str(runner['selectionId']), 'marketId': str(market_book[0]['marketId'])})
            price_list.append(price)
    price_list = sorted(price_list, key=lambda x: x['price'])
    return price_list[0]

def get_current_date():
    today = datetime.datetime.utcnow()
    today = today.strftime('%Y-%m-%dT')
    return today

def get_current_time():
    now = datetime.datetime.utcnow()
    return now.strftime('%H:%M:%S.%f')


if __name__ == '__main__':
    login_info = get_login_info(parameters.username, parameters.password)
    bf = BetfairExchange(login_info)
    json = parameters.list_market_catalogue_json()
    market_catalogue = bf.send_json_request(json)

    for market in market_catalogue:
        market_id = market['marketId']
        event_time = get_event_time(market)
        bf.schedule_orders(event_time, market_id)
    run_schedule()
