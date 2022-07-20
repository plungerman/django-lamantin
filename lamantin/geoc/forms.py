# -*- coding: utf-8 -*-

from django import forms

from lamantin.geoc.models import Course


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ('title', 'number', 'phile', 'outcome')
