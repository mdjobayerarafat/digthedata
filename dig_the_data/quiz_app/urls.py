from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    team_profile, submit_answer, request_hint, hint_requests, scoreboard, custom_404_view,
    TeamViewSet, QuizViewSet, QuestionViewSet, HintRequestViewSet, AnswerViewSet,
    TeamUserViewSet, HintViewSet, HintNotificationViewSet, SubmitAnswerAPI, ScoreboardAPI, LoginView, custom_500_view
)

# Django REST Framework Router for REST APIs
router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'hint-requests', HintRequestViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'team-users', TeamUserViewSet)
router.register(r'hints', HintViewSet)
router.register(r'hint-notifications', HintNotificationViewSet)

# Custom 404 handler
handler404 = custom_404_view
handler500 = custom_500_view

# URL patterns for web views and REST APIs
urlpatterns = [
    # Web Views
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login_view'),
    path('profile/', team_profile, name='team_profile'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
    path('submit_answer/<int:question_id>/', submit_answer, name='submit_answer'),
    path('request_hint/', request_hint, name='request_hint'),
    path('hint_requests/', hint_requests, name='hint_requests'),
path('home1', views.home, name='home'),
    path('register/', views.register, name='register'),

    path('user_login/', views.user_login_view, name='user_login'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('done/', views.done, name='done'),

    # REST APIs
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/', include(router.urls)),  # Includes all REST API routes registered in the router
    path('api/submit-answer/<int:question_id>/', SubmitAnswerAPI.as_view(), name='submit-answer-api'),
    path('api/scoreboard/', ScoreboardAPI.as_view(), name='scoreboard-api'),
]