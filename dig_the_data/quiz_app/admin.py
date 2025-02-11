from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Team, Quiz, Question, Score, HintRequest, TeamQuestion, Answer, TeamUser, Hint, SiteSettings, UserPerson
import logging

# Admin configuration for the Team model
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display team ID and name
    search_fields = ('name',)  # Enable search by team name
    fields = ('name', 'password')  # Include password in the admin form

    def save_model(self, request, obj, form, change):
        if obj.password:  # Only hash the password if it has been set
            obj.set_password(obj.password)  # Hash the password
        super().save_model(request, obj, form, change)  # Call the parent class's save_model method

    def get_readonly_fields(self, request, obj=None):
        if obj:  # If the object already exists, make the password field readonly
            return ['password']
        return []

# Admin configuration for the Quiz model
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active')  # Display quiz ID and active status
    list_filter = ('is_active',)  # Filter quizzes by active status

# Admin configuration for the Question model
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_type', 'question_text', 'common_question', 'active')  # Display question details
    list_filter = ('common_question', 'active', 'question_type')  # Filter options for questions
    search_fields = ('question_text', 'answer')  # Enable search by question text and answer

# Admin configuration for the TeamQuestion model
class TeamQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'question', 'hint_used', 'answered')  # Display team-question relationship details
    list_filter = ('team', 'answered')  # Filter by team and answered status
    raw_id_fields = ('team', 'question')  # Optimize for large datasets

# Admin configuration for the Score model
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'score')  # Display score details
    list_filter = ('team',)  # Filter scores by team

# Admin configuration for the Answer model
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('team', 'question', 'submitted_answer', 'score')  # Customize the fields to display
    search_fields = ('team__name', 'question__question_text')  # Enable search by team name and question text


# Register the models with the admin site
admin.site.register(Team, TeamAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(TeamQuestion, TeamQuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Hint)  # Register Hint model
admin.site.register(HintRequest)  # Register HintRequest model
admin.site.register(SiteSettings)  # Register SiteSettings model
admin.site.register(TeamUser)  # Register TeamUser model