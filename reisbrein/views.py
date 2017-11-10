from django import forms
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse


class PlanForm(forms.Form):
    from_location = forms.CharField(label='Van')
    to_location = forms.CharField(label='Naar')


class PlanInputView(FormView):
    template_name = 'reisbrein/plan_input.html'
    form_class = PlanForm
    success_url = '/thanks/'

    def form_valid(self, form):
        self.from_location = form.cleaned_data['from_location']
        self.to_location = form.cleaned_data['to_location']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('plan-results', args=(self.from_location, self.to_location)) #'/plan/results?from=' + self.from_location + '&to=' + self.to_location
