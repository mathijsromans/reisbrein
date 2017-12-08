import requests
import json
import time
import logging
from datetime import timedelta, datetime, timezone
from reisbrein.models import ApiCache

logger = logging.getLogger(__name__)


def query(url, params, headers, expiry):
    headers_str = json.dumps(headers)
    cache, created = ApiCache.objects.get_or_create(url=url, params=params, headers=headers_str)
    now = datetime.now(timezone.utc)
    if not created and now - cache.datetime_updated < expiry:
        logger.info('Retreiving ' + url + ' from cache')
        return json.loads(cache.result)
    logger.info('BEGIN query')
    log_start = time.time()
    logger.info('Query url=' + url)
    logger.info('Query params=' + str(params))
    # logger.info('Query headers=' + headers_str)
    response = requests.get(url, params, headers=headers)
    logger.info(response.url)
    result = response.json()
    cache.result = json.dumps(result)
    cache.save()
    log_end = time.time()
    logger.info('END query; time=' + str(log_end - log_start))
    return result
