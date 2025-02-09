import json
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Team, Quiz, Question, HintRequest, Answer, TeamUser, Hint, HintNotification
from .serializers import TeamSerializer, QuizSerializer, QuestionSerializer, HintRequestSerializer, AnswerSerializer, \
    TeamUserSerializer, HintSerializer, HintNotificationSerializer, LoginSerializer


# Web Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('team_profile')
    return render(request, 'login.html')

@login_required
def team_profile(request):
    team = Team.objects.get(user=request.user)
    quiz = Quiz.objects.first()
    team_users = TeamUser.objects.filter(team=team)

    return render(request, 'team_profile.html', {
        'team': team,
        'quiz': quiz,
        'team_users': team_users
    })

@login_required
def quiz_view(request):
    team = Team.objects.get(user=request.user)
    quiz = Quiz.objects.first()
    common_questions = Question.objects.filter(quiz=quiz, common_question=True)
    unique_questions = Question.objects.filter(teamquestion__team=team, common_question=False)
    submitted_answers = Answer.objects.filter(team=team)
    answered_questions = {answer.question.id: answer.question.correct_answer for answer in submitted_answers}

    return render(request, 'quiz.html', {
        'common_questions': common_questions,
        'unique_questions': unique_questions,
        'answered_questions': answered_questions or {},
        'team': team
    })

@require_POST
def submit_answer(request, question_id):
    try:
        data = json.loads(request.body)
        answer_text = data.get('answer')

        if not answer_text:
            return JsonResponse({'success': False, 'error': 'Answer cannot be empty.'}, status=400)

        question = get_object_or_404(Question, id=question_id)
        is_correct = (answer_text.strip().lower() == question.correct_answer.strip().lower())

        if is_correct:
            team = Team.objects.get(user=request.user)
            Answer.objects.create(
                team=team,
                question=question,
                submitted_answer=answer_text,
                is_correct=True,
                score=10 if question.common_question else 20
            )

        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def request_hint(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        question_id = request.POST.get('question_id')

        try:
            team = Team.objects.get(name=team_name)
            question = Question.objects.get(id=question_id)
            hint_request = HintRequest.objects.create(team=team, question=question)
            return redirect('hint_requests')
        except Team.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Team not found.'})
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found.'})

    user_team = Team.objects.get(user=request.user)
    questions = Question.objects.all()
    return render(request, 'request_hint.html', {'questions': questions, 'user_team': user_team})

@login_required
def hint_requests(request):
    hint = HintRequest.objects.filter(team__user=request.user)
    return render(request, 'hint_requests.html', {'hint_requests': hint})

def scoreboard(request):
    teams = Team.objects.all()
    scoreboard_data = []
    for team in teams:
        total_score = Answer.objects.filter(team=team).aggregate(total=Sum('score'))['total'] or 0
        hint_requests = HintRequest.objects.filter(team=team).count()
        approved_requests = HintRequest.objects.filter(team=team, is_fulfilled=True).count()
        answered_questions = Answer.objects.filter(team=team, is_correct=True).count()
        score_after_deduction = total_score - (approved_requests * 5)
        scoreboard_data.append({
            'team_name': team.name,
            'score': max(score_after_deduction, 0),
            'hint_requests': hint_requests,
            'approved_requests': approved_requests,
            'solved_questions': answered_questions,
        })

    scoreboard_data.sort(key=lambda x: (-x['score'], x['approved_requests']))
    return render(request, 'scoreboard.html', {'scoreboard_data': scoreboard_data})

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

# REST APIs
class LoginView(APIView):
    def post(self, request):
        print("Request data:", request.data)  # Debugging line
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        print("Serializer errors:", serializer.errors)  # Debugging line
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

class HintRequestViewSet(viewsets.ModelViewSet):
    queryset = HintRequest.objects.all()
    serializer_class = HintRequestSerializer
    permission_classes = [IsAuthenticated]

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]

class TeamUserViewSet(viewsets.ModelViewSet):
    queryset = TeamUser .objects.all()
    serializer_class = TeamUserSerializer
    permission_classes = [IsAuthenticated]

class HintViewSet(viewsets.ModelViewSet):
    queryset = Hint.objects.all()
    serializer_class = HintSerializer
    permission_classes = [IsAuthenticated]

class HintNotificationViewSet(viewsets.ModelViewSet):
    queryset = HintNotification.objects.all()
    serializer_class = HintNotificationSerializer
    permission_classes = [IsAuthenticated]

class SubmitAnswerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        try:
            answer_text = request.data.get('answer')
            if not answer_text:
                return Response({'success': False, 'error': 'Answer cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

            question = get_object_or_404(Question, id=question_id)
            is_correct = (answer_text.strip().lower() == question.correct_answer.strip().lower())

            if is_correct:
                team = Team.objects.get(user=request.user)
                Answer.objects.create(
                    team=team,
                    question=question,
                    submitted_answer=answer_text,
                    is_correct=True,
                    score=10 if question.common_question else 20
                )

            return Response({
                'success': True,
                'is_correct': is_correct,
            })

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ScoreboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teams = Team.objects.all()
        scoreboard_data = []
        for team in teams:
            total_score = Answer.objects.filter(team=team).aggregate(total=Sum('score'))['total'] or 0
            hint_requests = HintRequest.objects.filter(team=team).count()
            approved_requests = HintRequest.objects.filter(team=team, is_fulfilled=True).count()
            answered_questions = Answer.objects.filter(team=team, is_correct=True).count()
            score_after_deduction = total_score - (approved_requests * 5)
            scoreboard_data.append({
                'team_name': team.name,
                'score': max(score_after_deduction, 0),
                'hint_requests': hint_requests,
                'approved_requests': approved_requests,
                'solved_questions': answered_questions,
            })

        scoreboard_data.sort(key=lambda x: (-x['score'], x['approved_requests']))
        return Response(scoreboard_data)