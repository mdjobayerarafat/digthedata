from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Quiz(models.Model):
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Quiz {'Active' if self.is_active else 'Inactive'}"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=20, default='General')
    question_text = models.TextField(default='')
    link = models.URLField(blank=True, null=True)
    correct_answer = models.CharField(max_length=100, default='')
    common_question = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text[:50]

class TeamQuestion(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    hint_used = models.BooleanField(default=False)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team} - {self.question}"


class Score(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.team.name}: {self.score}"
class Answer(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submitted_answer = models.CharField(max_length=100, blank=False)
    score = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if not self.submitted_answer or self.submitted_answer.strip() == "":
            raise ValidationError("Submitted answer cannot be empty.")

        if self.question.common_question:
            self.score = 10
        else:
            self.score = 20


        self.is_correct = (self.submitted_answer.strip().lower() == self.question.correct_answer.strip().lower())


        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.team.name} - {self.question.question_text} - {self.submitted_answer} (Score: {self.score})"
class TeamUser (models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_users')
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    class_id = models.CharField(max_length=20)
    wp_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} - {self.position} ({self.team.name})"

class Hint(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    hint_text = models.TextField()

class HintRequest(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    hint = models.ForeignKey(Hint, null=True, blank=True, on_delete=models.SET_NULL)
    is_fulfilled = models.BooleanField(default=False)

    def __str__(self):
        return f"Hint request from {self.team.name} for {self.question.question_text}"

class HintNotification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message}"