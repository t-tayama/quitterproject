from django import forms
from .models import Quiz, Contact, Report

class QuizCreateForm(forms.ModelForm):

    class Meta:
        model = Quiz
        fields = (
            'title', 'text', 'image','category', 'tag',
            'choice_a', 'choice_b', 'choice_c', 'choice_d',
            'correct_answer', 'explanation'
            )


class ContactCreateForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = (
            'name','mail','message'
            )


class ReportCreateForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = (
           'report_category', 'message'
            )