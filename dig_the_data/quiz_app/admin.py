from django.contrib import admin
from .models import Team, Quiz, Question, Score, HintRequest, TeamQuestion, Answer, TeamUser, Hint


class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')  # Display team ID, name, and associated user

#class QuizAdmin(admin.ModelAdmin):
   # list_display = ('id', 'is_active')  # Display quiz ID and active status



#class QuestionAdmin(admin.ModelAdmin):
    #list_display = ('question_type', 'question_text', 'answer', 'common_question', 'active')
   # list_filter = ('common_question', 'active', 'question_type')
   # search_fields = ('question_text', 'answer')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active')  # Display quiz ID and active status

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_type', 'question_text', 'common_question', 'active')  # Display question details

class TeamQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'question', 'hint_used', 'answered')  # Display team-question relationship details


class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'score')  # Display score details


#class TeamQuestionAdmin(admin.ModelAdmin):
   # list_display = ('id', 'team', 'question', 'hint_used', 'answered')  # Display relevant fields
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('team', 'question', 'submitted_answer', 'score')  # Customize the fields to display
    search_fields = ('team__name', 'question__question_text')

class TeamUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'team', 'class_id', 'wp_number', 'email')  # Fields to display in the list view
    search_fields = ('name', 'email', 'team__name')  # Fields to search in the admin interface
    list_filter = ('team', 'position')

# Register the models with the admin site
admin.site.register(Team, TeamAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(TeamQuestion, TeamQuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(TeamUser , TeamUserAdmin)
admin.site.register(Hint)
admin.site.register(HintRequest)