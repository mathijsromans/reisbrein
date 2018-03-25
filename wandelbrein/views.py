import datetime
import time

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django import forms
from django.urls import reverse

from datetimewidget.widgets import DateTimeWidget

from reisbrein.generator.gen_common import FixTime
from reisbrein.views import PlanView
from reisbrein.models import UserTravelPreferences
from wandelbrein.planner import WandelbreinPlanner



class PlanViewReisbrein(TemplateView):
    template_name = 'wandelbrein/plan_results.html'

    def get_context_data(self, start, timestamp, **kwargs):
        user, user_preferences = PlanView.get_user_preferences(self.request)

        request_start = time.time()
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
        plans = p.solve(start, start_time, user_preferences)
        results = PlanView.get_results(plans)

        context = super().get_context_data()
        context['start'] = start
        context['end'] = ''
        context['arrive_by'] = fix_time == FixTime.END
        context['results'] = results
        return context


class PlanForm(forms.Form):
    start = forms.CharField(label='Van')
    date_time_widget = DateTimeWidget(attrs={'id':"yourdatetimeid"}, usel10n=True, bootstrap_version=3)
    leave = forms.DateTimeField(label='Vertrek', widget=date_time_widget)


class PlanInputView(FormView):
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
        self.timestamp_minutes = int(form.cleaned_data['leave'].timestamp()/60)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('wandel-plan-results', args=(self.start, str(self.timestamp_minutes)))
