import bfapi

APP_KEY = 'xxxx'
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
REQ_PREFIX = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/'
USERNAME = 'xxxx' 
PASSWORD = 'xxxx'

HORSE_KEYS = ['date', 'country', 'track', 'going', 'type', 'distance', 'class', 'time', 'stall', 'name', 'or', 'age', 'pace', 'weight', 'jockey', 'trainer', 'head gear', 'sp fav', 'industry sp', 'betfair sp', 'ip min', 'ip max', 'pre min', 'pre max', 'pred industry sp', 'place', 'winning distance', 'runners', 'sp win return', 'e/w return', 'bf win return']

def place_orders_json(market_id, selection_id, price):
    json = REQ_PREFIX + 'placeOrders","params": {"marketId": "' + str(market_id) + '","instructions": [{"selectionId": "' + str(selection_id) + '","handicap": "0.0","side": "BACK","orderType": "LIMIT","limitOrder": {"size": "2.0","price": "' + str(price) + '","persistenceType": "LAPSE"}}]}}'
    return json

def list_market_catalogue_json():
    today = bfapi.get_current_date()
    json = REQ_PREFIX + 'listMarketCatalogue", "params": {"filter": {"eventTypeIds": ["7"], "eventIds": [], "marketTypeCodes":["WIN"], "marketCountries": ["GB"], "marketStartTime":{"from": "' + today + '00:00:00Z", "to":"' + today + '23:59:00Z"}}, "maxResults": "200","marketProjection":["EVENT", "MARKET_START_TIME", "RUNNER_DESCRIPTION"]}}'
    return json

def list_market_book_json(market_id):
    json = REQ_PREFIX + 'listMarketBook", "params": {"marketIds":["' + market_id + '"],"priceProjection":{"priceData":["EX_BEST_OFFERS"], "matchProjection":["ROLLED_UP_BY_AVG_PRICE"], "orderProjection":["EXECUTABLE"] ,"virtualise": "true"}}}'        
    return json

def list_cleared_orders_json(date):
    json = REQ_PREFIX + 'listClearedOrders","params": {"betStatus":"SETTLED", "settledDateRange": {"from": "' + date + '00:00:00Z", "to":"' + date + '23:59:00Z"}}}'
    return json
