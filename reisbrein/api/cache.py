from recordclass import recordclass
from requests_futures.sessions import FuturesSession
from concurrent.futures import wait
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


Query = recordclass('Query',
                    ['result',
                     'url',
                     'arguments',
                     'headers',
                     'expiry'])

QueryInfo = recordclass('QueryInfo',
                        ['q',
                         'arguments_str',
                         'headers_str',
                         'update_cache',
                         'filename_to_be_updated'])

def make_str(coll):
    """
    :param coll: input dict or list
    :return: string that is always the same for coll: it does not depend on hashing
    """
    if isinstance(coll, dict):
        return str(sorted(coll.items(), key=lambda x: x[1]))
    return str(coll)


def try_get_from_cache(qi):
        now = datetime.now(timezone.utc)
        try:
            cache = ApiCache.objects.get(url=qi.q.url, params=qi.arguments_str, headers=qi.headers_str)
            expired = not ASSUME_NO_API_EXPIRY and now - cache.datetime_updated > qi.q.expiry
            if expired:
                cache.delete()
                qi.update_cache = True
            else:
                logging.info('Retreiving ' + qi.q.url + ' from cache')
                qi.q.result = json.loads(cache.result)
        except ApiCache.DoesNotExist:
            qi.update_cache = True


def try_get_from_file(qi):
        h = hashlib.md5((qi.q.url+qi.arguments_str+qi.headers_str).encode('utf-8')).hexdigest()
        o = urlparse(qi.q.url)
        filename = 'data/cache/' + o.netloc + '_' + h + '.dat'
        try:
            with open(filename, 'r') as json_file:
                qi.q.result = json.load(json_file)
        except OSError:
            qi.filename_to_be_updated = filename


def bg_cb(sess, resp):
    # parse the json storing the result on the response object
    resp.data = resp.json()


def do_queries(qis):
    to_do_qi = [qi for qi in qis if not qi.q.result]
    if not to_do_qi:
        return
    logger.info('BEGIN query ' + to_do_qi[0].q.url + ' (' + str(len(to_do_qi)) + ')')
    log_start = time.time()
    session = FuturesSession(max_workers=len(to_do_qi))
    futures = [
        session.get(qi.q.url, params=qi.q.arguments, headers=qi.q.headers,
                    background_callback=bg_cb)
        for qi in to_do_qi
    ]
    wait(futures)
    for item in zip(to_do_qi, futures):
        item[0].q.result = item[1].result().data
    log_end = time.time()
    logger.info('END query; time=' + str(log_end - log_start))


def query_list(queries):
    qis = [QueryInfo(q, make_str(q.arguments), make_str(q.headers), False, '') for q in queries]
    for qi in qis:
        qi.q.result = None
        try_get_from_cache(qi)
        if not qi.q.result and TESTING_FROM_CMD_LINE:
            try_get_from_file(qi)

    do_queries(qis)

    for qi in qis:
        if qi.update_cache:
            cache, created = ApiCache.objects.get_or_create(url=qi.q.url, params=qi.arguments_str, headers=qi.headers_str)
            cache.result = json.dumps(qi.q.result)
            cache.save()

        if qi.filename_to_be_updated:
            os.makedirs(os.path.dirname(qi.filename_to_be_updated), exist_ok=True)
            with open(qi.filename_to_be_updated, 'w') as json_file:
                json.dump(qi.q.result, json_file)


def query(url, arguments, headers, expiry):
    q = Query(None, url, arguments, headers, expiry)
    query_list([q])
    return q.result

