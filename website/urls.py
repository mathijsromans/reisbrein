from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from reisbrein.views import PlanInputView
from reisbrein.views import PlanView
from reisbrein.views import UserTravelPreferencesView

from website.views import ContactView
from website.views import UserProfileView


urlpatterns = [
    url(r'^$', PlanInputView.as_view(), name='plan-input'),
    url(r'^reisadvies/(?P<start>.+)/(?P<end>.+)$', PlanView.as_view(), name='plan-results'),

    url(r'^about/$', TemplateView.as_view(template_name="website/about.html"), name='about'),

    url(r'^travel/preferences/$', login_required(UserTravelPreferencesView.as_view()), name='user-travel-preferences'),

    url(r'^userprofile/(?P<pk>[0-9]+)/$', login_required(UserProfileView.as_view()), name='userprofile'),

    url(r'^accounts/', include('registration.backends.simple.urls')),  # the django-registration module
    url(r'^admin/', admin.site.urls),
]


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ]
