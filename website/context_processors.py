from website import __version__


def info(request):
    return {
        'project_version': __version__,
        'is_anonymous_user': request.user.groups.filter(name='anonymous').exists(),
    }
