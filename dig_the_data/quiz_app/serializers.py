from rest_framework import serializers
from .models import Team, Quiz, Question, HintRequest, Answer, TeamUser, Hint, HintNotification

from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Team, Quiz, Question, HintRequest, Answer, TeamUser , Hint, HintNotification

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'  # or specify the fields you want to include

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'  # or specify the fields you want to include

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'  # or specify the fields you want to include

class HintRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HintRequest
        fields = '__all__'  # or specify the fields you want to include

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'  # or specify the fields you want to include

class TeamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamUser
        fields = '__all__'  # or specify the fields you want to include

class HintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hint
        fields = '__all__'  # or specify the fields you want to include

class HintNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HintNotification
        fields = '__all__'  # or specify the fields you want to include

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)