# -*- coding: utf-8 -*-
import logging
import re

from django import forms
from djtools.fields import BINARY_CHOICES
from lamantin.geoc.models import Annotation
from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome
from lamantin.geoc.models import Document
from lamantin.geoc.models import Outcome

logger = logging.getLogger('debug_logfile')
# regex for course number: HIS 420X, PHL 4200, etc
COURSE_NUMBER = re.compile(r"[A-Za-z][A-Za-z][A-Za-z]\s\d\d\d[A-Za-z0-9]", re.IGNORECASE)


class Dupes:
    """Data model for managing form validation for outcomes."""

    def __init__(self):
        """Initialize the object with defauls."""
        self.tags = {
            'Abilities': {'outcomes': [], 'check': False},
            'Explorations': {'outcomes': [], 'check': False},
            'Perspectives': {'outcomes': [], 'check': False},
        }
        self.error = []

    def get_outcomes(self):
        """Fetch the outcome objects for each tag."""
        for tag, outcomes in self.tags.items():
            self.tags[tag]['outcomes'] = Outcome.objects.filter(tags__name__in=[tag])

    def check(self, outcomes):
        """Check for dupes."""
        for outcome in outcomes:
            for tag, slo in self.tags.items():
                if outcome in slo['outcomes']:
                    if not slo['check']:
                        slo['check'] = True
                    else:
                        if tag not in self.error:
                            self.error.append(tag)


class CourseForm(forms.ModelForm):
    """GEOC course form."""

    outcome = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Outcome.objects.all(),
        required=True,
    )
    multipass = forms.TypedChoiceField(
        label="I am submitting multiple courses under the same SLO's",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
        help_text="""
            You may submit multiple courses (cross list) if those courses
            substantially fulfill the same SLO categories within the GE structure.
            If any of the courses you are submitting also carry another designation,
            they would need to be submitted individually.
        """
    )
    crosslist1 = forms.CharField(
        label="Cross list 1: course number",
        required=False,
        help_text="FORMAT: AAA 1234 or AAA 123X e.g. HIS 4200, BIO 420T",
    )
    crosslist2 = forms.CharField(
        label="Cross list 2: course number",
        required=False,
        help_text="FORMAT: AAA 1234 or AAA 123X e.g. HIS 4200, BIO 420T",
    )
    crosslist3 = forms.CharField(
        label="Cross list 3: course number",
        required=False,
        help_text="FORMAT: AAA 1234 or AAA 123X e.g. HIS 4200, BIO 420T",
    )
    crosslist4 = forms.CharField(
        label="Cross list 4: course number",
        required=False,
        help_text="FORMAT: AAA 1234 or AAA 123X e.g. HIS 4200, BIO 420T",
    )

    class Meta:
        model = Course
        fields = ('title', 'number', 'outcome', 'multipass')
        widgets = {
            'number': forms.TextInput(attrs={'style': 'text-transform:uppercase'}),
        }

    def clean(self):
        """Form validation."""
        cd = self.cleaned_data
        # multipass validation for crosslisted courses
        logger.debug('crosslist1 = {0}'.format(cd.get('crosslist1')))
        crosslist = {
            'crosslist1': cd.get('crosslist1'),
            'crosslist2': cd.get('crosslist2'),
            'crosslist3': cd.get('crosslist3'),
            'crosslist4': cd.get('crosslist4'),
        }
        error = 'Course numbers should be in the format: AAA 1234 or AAA 123X'
        if cd.get('multipass') == 'Yes':
            if (
                    not crosslist['crosslist1'] and
                    not crosslist['crosslist2'] and
                    not crosslist['crosslist3'] and
                    not crosslist['crosslist4']
                ):
                error = True
                self.add_error('multipass', 'Please provide at least one crosslisted course')
            else:
                for key, value in crosslist.items():
                    if value and not COURSE_NUMBER.match(value):
                        self.add_error(key, error)
        # verify that there is only one outcome per SLO
        dupes = Dupes()
        dupes.get_outcomes()
        if cd.get('outcome'):
            dupes.check(cd['outcome'])
        if dupes.error:
            self.add_error('outcome', 'One of the SLO groups have more than one outcome selected')
        return cd

    def clean_number(self):
        """Form validation for course number field."""
        cd = self.cleaned_data
        number = cd.get('number')
        if not COURSE_NUMBER.match(number):
            self.add_error('number', 'Course numbers should be in the format: AAA 1234 or AAA 123X')
        return cd


class CourseOutcomeForm(forms.ModelForm):
    """GEOC specific outcome form."""

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(CourseOutcomeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = CourseOutcome
        fields = ['description']

    def clean(self):
        """Form validation."""
        cd = self.cleaned_data
        if self.request.POST.get('save_submit') and not cd.get('description'):
             self.add_error('description', 'Please provide a description')
        return cd


class AnnotationForm(forms.ModelForm):
    """GEOC document required fields."""

    body = forms.CharField(
        label="Please provide your feedback for this course",
        widget=forms.Textarea,
    )

    class Meta:
        model = Annotation
        fields = ['body']


class DocumentForm(forms.ModelForm):
    """GEOC documents."""

    phile = forms.FileField(
        label="Supplimentary file",
        help_text="""
            (Optional) If you believe it may be necessary to provide
            context or additional information, you may upload a syllabus
            or course proposal for the course here. If it is necessary
            to upload multiple files, you may do so after saving a draft
            or after submission by clicking the icon next to "Documents".
            Alternatively, you may provide links to a folder or documents
            in the final response box of the form.
        """,
        required=False,
    )

    class Meta:
        model = Document
        fields = ['phile', 'name']


class DocumentRequiredForm(DocumentForm):
    """GEOC document required fields."""

    phile = forms.FileField(
        label="File",
        required=True,
    )
    name = forms.CharField(required=True)
