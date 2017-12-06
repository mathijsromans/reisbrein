import requests
import json
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
    logger.info('New query ' + url)
    response = requests.get(url, params, headers=headers)
    result = response.json()
    cache.result = json.dumps(result)
    cache.save()
    return result
