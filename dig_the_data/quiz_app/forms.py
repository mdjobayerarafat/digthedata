from django import forms
from .models import Answer

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['team', 'question', 'submitted_answer', 'score']

    def clean_submitted_answer(self):
        submitted_answer = self.cleaned_data.get('submitted_answer')
        if not submitted_answer or submitted_answer.strip() == "":
            raise forms.ValidationError("Submitted answer cannot be empty.")
        return submitted_answer