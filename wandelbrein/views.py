import datetime
import logging

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django import forms
from django.urls import reverse
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetimewidget.widgets import DateTimeWidget

from reisbrein.generator.gen_common import FixTime
from reisbrein.views import PlanView
from reisbrein.views import PlanInputView
from reisbrein.models import UserTravelPreferences
from wandelbrein.models import Trail
from wandelbrein.planner import WandelbreinPlanner

logger = logging.getLogger(__name__)


class PlanViewWandelbrein(TemplateView):
    template_name = 'wandelbrein/plan_results.html'

    def get_context_data(self, start, timestamp, **kwargs):
        user, user_preferences = PlanView.get_user_preferences(self.request)

        fix_time = FixTime.START
        if timestamp[-1].isalpha:
            if timestamp[-1] == 'a':
                fix_time = FixTime.END
            timestamp = timestamp[:-1]
        if not timestamp or timestamp == '0':
            start_time = datetime.datetime.now()
        else:
            start_time = datetime.datetime.fromtimestamp(60*float(timestamp))

        p = WandelbreinPlanner()
        plans, trail = p.solve(start, start_time, user_preferences)
        results = PlanView.get_results(plans)

        context = super().get_context_data()
        context['trail'] = trail
        context['start'] = start
        context['end'] = ''
        context['arrive_by'] = fix_time == FixTime.END
        context['results'] = results
        return context


class PlanForm(forms.Form):
    start = forms.CharField(label='Van')
    date_time_widget = DateTimeWidget(attrs={'id':"yourdatetimeid"}, usel10n=True, bootstrap_version=3)
    leave = forms.DateTimeField(label='Vertrek', widget=date_time_widget)


class PlanInputWandelView(FormView):
    template_name = 'wandelbrein/plan_input.html'
    form_class = PlanForm

    def __init__(self):
        super().__init__()
        self.start = ''
        self.timestamp_minutes = 0

    def get_initial(self):
        initial = super().get_initial()
        if not self.request.user.is_authenticated:
            return initial
        user_preferences, created = UserTravelPreferences.objects.get_or_create(user=self.request.user)
        initial['start'] = user_preferences.home_address
        initial['leave'] = datetime.datetime.now()
        return initial

    def form_valid(self, form):
        self.start = form.cleaned_data['start']
        PlanInputView.set_home_address_if_empty(self.request.user, self.start)
        self.timestamp_minutes = int(form.cleaned_data['leave'].timestamp()/60)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('wandel-plan-results', args=(self.start, str(self.timestamp_minutes) + 'd'))


class TrailDetailsView(TemplateView):
    template_name = 'wandelbrein/trail_details.html'

    def get_context_data(self, trail_id, **kwargs):
        trail = Trail.objects.get(id=trail_id)
        context = super().get_context_data()
        context['trail'] = trail
        return context


class TrailsView(TemplateView):
    template_name = 'wandelbrein/trails.html'

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page', 1)
        trails = Trail.objects.all()
        trails_per_page = 9
        paginator = Paginator(trails, trails_per_page)
        try:
            trails = paginator.page(page)
        except PageNotAnInteger:
            trails = paginator.page(1)
        except EmptyPage:
            trails = paginator.page(paginator.num_pages)
        context = super().get_context_data()
        context['trails'] = trails
        return context


def get_gpx(request, trail_id):
    trail = Trail.objects.get(id=trail_id)
    return HttpResponse(trail.gpx)
