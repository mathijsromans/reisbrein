import datetime
import time
from django.views.generic import TemplateView
from reisbrein.generator.gen_common import FixTime
from reisbrein.views import PlanView
from wandelbrein.planner import WandelbreinPlanner


class PlanViewReisbrein(TemplateView):

    template_name = 'reisbrein/plan_results.html'

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