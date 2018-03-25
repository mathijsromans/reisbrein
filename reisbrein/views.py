import datetime
import time
import logging
from django import forms
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from datetimewidget.widgets import DateTimeWidget
from reisbrein.generator.gen_common import FixTime
from reisbrein.primitives import Location
from reisbrein.planner import Planner
from reisbrein.models import UserTravelPreferences
from reisbrein.models import UserTravelPlan, Request
from .auth import create_and_login_anonymous_user

logger = logging.getLogger(__name__)


def validate_location(value):
    location = Location(value)
    if not location.gps or location.gps == (0,0):
        raise ValidationError(
            '{0} is not a valid location'.format(value),
            params={'value': value},
        )


class PlanForm(forms.Form):
    start = forms.CharField(label='Van', validators=[validate_location])
    end = forms.CharField(label='Naar', validators=[validate_location])
    date_time_widget = DateTimeWidget(attrs={'id':"yourdatetimeid"}, usel10n=True, bootstrap_version=3)
    leave = forms.DateTimeField(label='Vertrek', widget=date_time_widget)
    arrive_by = forms.BooleanField(label='Is aankomsttijd', required=False, widget=forms.HiddenInput())


class PlanInputView(FormView):
    template_name = 'reisbrein/plan_input.html'
    form_class = PlanForm

    def __init__(self):
        super().__init__()
        self.start = ''
        self.end = ''
        self.timestamp_minutes = 0
        self.arrive_by = False

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            create_and_login_anonymous_user(request)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if not self.request.user.is_authenticated:
            return initial
        user_preferences, created = UserTravelPreferences.objects.get_or_create(user=self.request.user)
        initial['start'] = user_preferences.home_address
        initial['leave'] = datetime.datetime.now()
        initial['arrive_by'] = False
        return initial

    def form_valid(self, form):
        self.start = form.cleaned_data['start']
        self.end = form.cleaned_data['end']
        self.timestamp_minutes = int(form.cleaned_data['leave'].timestamp()/60)
        self.arrive_by = form.cleaned_data['arrive_by']
        return super().form_valid(form)

    def get_success_url(self):
        fix = 'a' if self.arrive_by else 'd'
        return reverse('plan-results', args=(self.start, self.end, str(self.timestamp_minutes) + fix))

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        plan_history = []
        if self.request.user.is_authenticated:
            plan_history = UserTravelPlan.objects.filter(user=self.request.user)[:5]
        context['plan_history'] = plan_history
        return context


class PlanViewReisbrein(TemplateView):

    template_name = 'reisbrein/plan_results.html'

    def get_context_data(self, start, end, timestamp, **kwargs):
        user, user_preferences = PlanView.get_user_preferences(self.request)
        PlanView.register_request(start, end, user)

        request_start = time.time()
        fix_time = FixTime.START
        if timestamp[-1].isalpha:
            if timestamp[-1] == 'a':
                fix_time = FixTime.END
            timestamp = timestamp[:-1]
        if not timestamp or timestamp == '0':
            req_time = datetime.datetime.now()
        else:
            req_time = datetime.datetime.fromtimestamp(60*float(timestamp))

        p = Planner()
        plans = p.solve(start, end, req_time, fix_time, user_preferences)
        results = PlanView.get_results(plans)
        request_end = time.time()
        Request.objects.create(user=user, start=start, end=end, timedelta=request_end - request_start)

        context = super().get_context_data()
        context['start'] = start
        context['end'] = end
        context['arrive_by'] = fix_time == FixTime.END
        context['results'] = results
        return context


class PlanView():

    @staticmethod
    def register_request(start, end, user):
        plan, created = UserTravelPlan.objects.get_or_create(
            user=user,
            start=start,
            end=end
        )
        if not created:
            plan.save()  # update datetime updated

    @staticmethod
    def get_user_preferences(request):
        user_preferences = UserTravelPreferences()
        user = None
        if request.user.is_authenticated:
            user = request.user
            user_preferences, created = UserTravelPreferences.objects.get_or_create(user=user)
        return user, user_preferences

    @staticmethod
    def get_results(plans):
        max_time = PlanView.max_travel_time(plans)
        if max_time == 0:
            return []

        result = []
        for plan in plans:
            time = PlanView.travel_time(plan)
            segments = []
            for segment in plan.route:
                segments.append(
                    {
                        'obj': segment,
                        'travel_time_min': int(segment.time_sec/60),
                        'travel_time_str': PlanView.format_minutes(int(segment.time_sec/60)),
                        'travel_time_percentage': 100*segment.time_sec / time,
                    })
            result.append(
            {
                'travel_time_min': int(time/60),
                'arrival_time': plan.route[-1].to_vertex.time,
                'travel_time_str': PlanView.format_minutes(int(time/60)),
                'travel_time_percentage': 100*time/max_time,
                'segments': segments
            })
        return result

    @staticmethod
    def format_minutes(minutes):
        hours = minutes // 60
        minutes %= 60
        return "%2i:%02i" % (hours, minutes)


    @staticmethod
    def max_travel_time(plans):
        max_travel_time = 0
        for plan in plans:
            max_travel_time = max(max_travel_time, PlanView.travel_time(plan))
        return max_travel_time

    @staticmethod
    def travel_time(plan):
        time = 0
        for segment in plan.route:
            time += segment.time_sec
        return time


class UserTravelPreferencesForm(forms.Form):
    home_address = forms.CharField(label='Huisadres', required=False)
    has_car = forms.BooleanField(label='Ik heb een auto', required=False)
    avoid_highways = forms.BooleanField(label='Snelwegen vermijden', required=False)
    has_bicycle = forms.BooleanField(label='Ik heb een fiets', required=False)
    likes_to_bike = forms.IntegerField()
    travel_time_importance = forms.IntegerField()
    save_CO2 = forms.IntegerField(label='Duurzaamheid')
    show_n_results = forms.IntegerField(label='Aantal resultaten')
    #reduce_number_of_transfers = forms.BooleanField(label='Avoid transfers where it makes sense', required=False)


class UserTravelPreferencesView(FormView):
    form_class=UserTravelPreferencesForm
    template_name = 'reisbrein/user_travel_preferences.html'

    def get_initial(self):
        user_preferences, created = UserTravelPreferences.objects.get_or_create(user=self.request.user)
        initial = super().get_initial()
        initial['home_address'] = user_preferences.home_address
        initial['show_n_results'] = user_preferences.show_n_results
        initial['has_car'] = user_preferences.has_car
        initial['avoid_highways'] = user_preferences.avoid_highways
        initial['has_bicycle'] = user_preferences.has_bicycle
        initial['likes_to_bike'] = user_preferences.likes_to_bike
        initial['travel_time_importance'] = user_preferences.travel_time_importance
        initial['save_CO2'] = user_preferences.save_CO2
        #initial['reduce_number_of_transfers'] = user_preferences.reduce_number_of_transfers
        return initial

    def form_valid(self, form):
        user_preferences, created = UserTravelPreferences.objects.get_or_create(user=self.request.user)
        user_preferences.home_address = form.cleaned_data['home_address']
        user_preferences.show_n_results = form.cleaned_data['show_n_results']
        user_preferences.has_car = form.cleaned_data['has_car']
        user_preferences.avoid_highways = form.cleaned_data['avoid_highways']
        user_preferences.has_bicycle = form.cleaned_data['has_bicycle']
        user_preferences.likes_to_bike = form.cleaned_data['likes_to_bike']
        user_preferences.travel_time_importance = form.cleaned_data['travel_time_importance']
        user_preferences.save_CO2 = form.cleaned_data['save_CO2']
        #user_preferences.reduce_number_of_transfers = form.cleaned_data['reduce_number_of_transfers']
        user_preferences.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('plan-input')
