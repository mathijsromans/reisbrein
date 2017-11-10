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
        context['start'] = start
        context['end'] = end
        return context
