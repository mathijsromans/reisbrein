import datetime
import time
from django.views.generic import TemplateView
from reisbrein.generator.gen_common import FixTime
from reisbrein.models import UserTravelPlan, Request
from reisbrein.views import PlanView
from wandelbrein.planner import WandelbreinPlanner

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

        p = WandelbreinPlanner()
        # leave = datetime.datetime(year=2017, month=12, day=11, hour=9, minute=20, second=0)
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