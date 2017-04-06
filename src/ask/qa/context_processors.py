from django.core.cache import cache
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static


def default_avatar(request):
    avatar = cache.get('default_avatar', False)
    if not avatar:
        avatar = static(settings.DEFAULT_USER_AVATAR)
    return {
        'default_avatar': avatar
    }
