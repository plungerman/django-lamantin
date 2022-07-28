# -*- coding: utf-8 -*-

from django import forms

from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome
from lamantin.geoc.models import Document
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
        fields = ('title', 'number', 'outcome')

    def clean(self):
        """Form validation."""
        cd = self.cleaned_data
        return cd


class CourseOutcomeForm(forms.ModelForm):
    """GEOC specific outcome form."""

    class Meta:
        model = CourseOutcome
        fields = ('description',)


class DocumentForm(forms.ModelForm):
    """GEOC documents."""

    class Meta:
        model = Document
        fields = ['phile']
