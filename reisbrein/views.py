from django import forms
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse


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
        return reverse('plan-results', args=(self.from_location, self.to_location))


class PlanView(TemplateView):
    template_name = 'reisbrein/plan_results.html'

    def get_context_data(self, start, end, **kwargs):
        context = super().get_context_data()
        results = [
            {
                'travel_time_min': 46,
                'travel_time_percentage': 85,
                'steps': [
                    {
                        'start': start,
                        'end': end,
                        'type': 'Auto',
                        'travel_time_min': 46,
                        'travel_time_percentage': 100,
                    },
                ]
            },
            {
                'travel_time_min': 54,
                'travel_time_percentage': 100,
                'steps':[
                    {
                        'start': start,
                        'end': 'Utrecht Centraal',
                        'type': 'Fiets',
                        'travel_time_min': 10,
                        'travel_time_percentage': 19,
                    }, {
                        'start': 'Utrecht Centraal',
                        'end': 'Amsterdam Centraal',
                        'type': 'Trein',
                        'travel_time_min': 32,
                        'travel_time_percentage': 59
                    }, {
                        'start': start,
                        'end': end,
                        'type': 'Fiets',
                        'travel_time_min': 12,
                        'travel_time_percentage': 22
                    }
                ]
            }
        ]
        context['start'] = start
        context['end'] = end
        context['results'] = results
        return context
