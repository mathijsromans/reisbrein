import requests
import json
import time
import logging
import hashlib
import os
from datetime import timedelta, datetime, timezone
from urllib.parse import urlparse
from reisbrein.models import ApiCache
from website.settings import TESTING_FROM_CMD_LINE, ASSUME_NO_API_EXPIRY

logger = logging.getLogger(__name__)


def do_query(url, params, headers):
    log_start = time.time()
    logger.info('BEGIN query')
    # logger.info('Query url=' + url)
    # logger.info('Query params=' + str(params))
    # logger.info('Query headers=' + headers_str)
    response = requests.get(url, params, headers=headers)
    logger.info(response.url)
    log_end = time.time()
    logger.info('END query; time=' + str(log_end - log_start))
    return response.json()


def make_str(coll):
    """
    :param coll: input dict or list
    :return: string that is always the same for coll: it does not depend on hashing
    """
    if isinstance(coll, dict):
        return str(sorted(coll.items(), key=lambda x: x[1]))
    return str(coll)


def query_list(url, queries, headers, expiry):
    for q in queries:
        q.result = query_from_session(url, q.arguments, headers, expiry)


def query(url, arguments, headers, expiry):
    return query_from_session(url, arguments, headers, expiry)

def query_from_session(url, arguments, headers, expiry):
    now = datetime.now(timezone.utc)
    # print(url)
    # print(params)
    # print(headers)

    arguments_str = make_str(arguments)
    headers_str = make_str(headers)

    # try to retreive from database
    cache, created = ApiCache.objects.get_or_create(url=url, params=arguments_str, headers=headers_str)
    expired = not ASSUME_NO_API_EXPIRY and now - cache.datetime_updated > expiry
    if not created and not expired:
        logger.info('Retreiving ' + url + ' from cache')
        return json.loads(cache.result)

    if TESTING_FROM_CMD_LINE:
        # try to retreive from disk
        # print (url+params_str+headers_str + ' -> ' + hashlib.md5((url+params_str+headers_str).encode('utf-8')).hexdigest())
        h = hashlib.md5((url+arguments_str+headers_str).encode('utf-8')).hexdigest()
        o = urlparse(url)
        filename = 'data/cache/' + o.netloc + '_' + h + '.dat'
        try:
            with open(filename, 'r') as json_file:
                result = json.load(json_file)
        except OSError:
            result = do_query(url, arguments, headers)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as json_file:
                json.dump(result, json_file)
    else:
        result = do_query(url, arguments, headers)

    cache.result = json.dumps(result)
    cache.save()

    return result
