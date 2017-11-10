from django import forms
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from reisbrein.planner import Planner


class PlanForm(forms.Form):
    start = forms.CharField(label='Van')
    end = forms.CharField(label='Naar')


class PlanInputView(FormView):
    template_name = 'reisbrein/plan_input.html'
    form_class = PlanForm

    def form_valid(self, form):
        self.start = form.cleaned_data['start']
        self.end = form.cleaned_data['end']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('plan-results', args=(self.start, self.end))


class PlanView(TemplateView):
    template_name = 'reisbrein/plan_results.html'

    def get_context_data(self, start, end, **kwargs):
        context = super().get_context_data()
        p = Planner()
        options = p.solve(start, end)
        results = self.get_results(options)

        context['start'] = start
        context['end'] = end
        context['results'] = results
        return context

    @staticmethod
    def get_results(options):
        max_time = PlanView.max_travel_time(options)
        if max_time == 0:
            return []

        result = []
        for option in options:
            time = PlanView.travel_time(option)
            segments = []
            for segment in option:
                segments.append(
                    {
                        'segment': segment.from_vertex,
                        'end': segment.to_vertex,
                        'type': segment.transport_type.name,
                        'travel_time_min': segment.distance,
                        'travel_time_percentage': 100*segment.distance / time,
                    })
            result.append(
            {
                'travel_time_min': time,
                'travel_time_percentage': 100*time/max_time,
                'segments': segments
            })
        return result


    @staticmethod
    def max_travel_time(options):
        max_travel_time = 0
        for option in options:
            max_travel_time = max(max_travel_time, PlanView.travel_time(option))
        return max_travel_time

    @staticmethod
    def travel_time(option):
        time = 0
        for segment in option:
            time += segment.distance
        return time

