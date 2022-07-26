# -*- coding: utf-8 -*-

from django import forms

#from django_summernote.widgets import SummernoteInplaceWidget
#from django_summernote.widgets import SummernoteWidget
#from django_summernote.fields import SummernoteTextField
from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome
from lamantin.geoc.models import Outcome


class CourseForm(forms.ModelForm):
    """GEOC course form."""

    outcome = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Outcome.objects.all(),
        required=True,
    )

    class Meta:
        model = Course
        fields = ('title', 'number', 'phile', 'outcome')

    def clean(self):
        """Form validation."""
        cd = self.cleaned_data
        return cd


class CourseOutcomeForm(forms.ModelForm):
    """GEOC specific outcome form."""

    #description = SummernoteTextField(
    #    help_text="Please indicate how this course meets this SLO.",
    #)


    class Meta:
        model = CourseOutcome
        fields = ('description',)
        #widgets = {
            #'description': SummernoteWidget(),
            #'description': SummernoteInplaceWidget(),
        #}
'''
class CourseOutcomeForm(forms.Form):
    """GEOC outcome form."""

    slo1 = forms.TextField(required=False)
    slo2 = forms.TextField(required=False)
    slo3 = forms.TextField(required=False)
    slo4 = forms.TextField(required=False)
    slo5 = forms.TextField(required=False)
    slo6 = forms.TextField(required=False)
'''
