from website import __version__
from website import settings


def info(request):
    return {
        'project_version': __version__,
        'is_anonymous_user': request.user.groups.filter(name='anonymous').exists(),
    }


def piwik(request):
    return {
        'piwik_url': settings.PIWIK_URL,
        'piwik_site_id': settings.PIWIK_SITE_ID
    }
