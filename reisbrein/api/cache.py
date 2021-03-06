from requests_futures.sessions import FuturesSession
from concurrent.futures import wait
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


class Query:
    def __init__(self, url, arguments, headers, expiry):
        self.url = url
        self.arguments = arguments
        self.headers = headers
        self.expiry = expiry
        self.result = None

    def full_url(self):
        return requests.Request('GET', self.url, params=self.arguments).prepare().url


class QueryInfo:
    def __init__(self, q):
        self.q = q
        self.arguments_str = make_str(q.arguments)
        self.headers_str = make_str(q.headers)
        self.update_cache = False
        self.filename_to_be_updated = ''


def make_str(coll):
    """
    :param coll: input dict or list
    :return: string that is always the same for coll: it does not depend on hashing
    """
    if isinstance(coll, dict):
        return str(sorted(coll.items(), key=lambda x: x[1]))
    return str(coll)


def try_get_from_database(qi):
        now = datetime.now(timezone.utc)
        try:
            cache = ApiCache.objects.get(url=qi.q.url, params=qi.arguments_str, headers=qi.headers_str)
            expired = not ASSUME_NO_API_EXPIRY and now - cache.datetime_updated > qi.q.expiry
            if expired or not cache.result:
                cache.delete()
                qi.update_cache = True
            else:
                logging.info('Retreiving ' + qi.q.url + ' from cache')
                qi.q.result = json.loads(cache.result)
        except ApiCache.DoesNotExist:
            qi.update_cache = True


def remove_from_database(qi):
    ApiCache.objects.filter(url=qi.q.url, params=qi.arguments_str, headers=qi.headers_str).delete()


def get_filename(qi):
    h = hashlib.md5((qi.q.url+qi.arguments_str+qi.headers_str).encode('utf-8')).hexdigest()
    o = urlparse(qi.q.url)
    return 'data/cache/' + o.netloc + '_' + h + '.dat'


def try_get_from_file(qi):
    filename = get_filename(qi)
    try:
        with open(filename, 'r') as json_file:
            qi.q.result = json.load(json_file)
    except OSError:
        qi.filename_to_be_updated = filename


def remove_from_file(qi):
    filename = get_filename(qi)
    try:
        os.remove(filename)
    except OSError:
        pass


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
    # for f in futures:
    #     print(f.result().url)
    for item in zip(to_do_qi, futures):
        item[0].q.result = item[1].result().data
    log_end = time.time()
    logger.info('END query; time=' + str(log_end - log_start))


def query_list(queries):
    qis = [QueryInfo(q) for q in queries]
    for qi in qis:
        qi.q.result = None
        try_get_from_database(qi)
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


def query_from(url, arguments, headers, expiry):
    q = Query(url, arguments, headers, expiry)
    return query(q)


def query(q):
    query_list([q])
    return q.result


def remove_cache(q):
    qi = QueryInfo(q)
    remove_from_database(qi)
    remove_from_file(qi)
