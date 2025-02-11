from django import forms
from .models import Answer, UserPerson


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['team', 'question', 'submitted_answer', 'score']

    def clean_submitted_answer(self):
        submitted_answer = self.cleaned_data.get('submitted_answer')
        if not submitted_answer or submitted_answer.strip() == "":
            raise forms.ValidationError("Submitted answer cannot be empty.")
        return submitted_answer

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserPerson
        fields = ['name', 'class_id', 'department', 'wp_number', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
        return user