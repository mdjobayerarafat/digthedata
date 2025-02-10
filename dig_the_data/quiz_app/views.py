import json
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from asgiref.sync import sync_to_async
from .models import Team, Quiz, Question, HintRequest, Answer, TeamUser , Hint, HintNotification
from .serializers import TeamSerializer, QuizSerializer, QuestionSerializer, HintRequestSerializer, AnswerSerializer, \
    TeamUser, HintNotificationSerializer, HintSerializer, TeamUserSerializer, LoginSerializer

Serializer, HintSerializer, HintNotificationSerializer, LoginSerializer

# Web Views
json_response_async = sync_to_async(JsonResponse)
async def final_round(request):
    return render(request, 'home.html')

async def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = await sync_to_async(authenticate)(request, username=username, password=password)

        if user:
            await sync_to_async(login)(request, user)
            return redirect('team_profile')

    return render(request, 'login.html')


@login_required
async def team_profile(request):
    # Wrap the entire queryset execution in sync_to_async
    get_team = sync_to_async(lambda: Team.objects.get(user=request.user))
    get_quiz = sync_to_async(lambda: Quiz.objects.first())
    get_team_users = sync_to_async(lambda: list(TeamUser.objects.filter(team=team)))

    team = await get_team()
    quiz = await get_quiz()
    team_users = await get_team_users()

    return render(request, 'team_profile.html', {
        'team': team,
        'quiz': quiz,
        'team_users': team_users
    })


from django.template.loader import render_to_string
from django.http import HttpResponse
from asgiref.sync import sync_to_async


async def render_async(request, template_name, context=None, status=200):
    """
    Asynchronously render a template and return an HttpResponse.

    :param request: The HTTP request object.
    :param template_name: The name of the template to render.
    :param context: A dictionary of context variables to pass to the template.
    :param status: The HTTP status code to return.
    :return: An HttpResponse object.
    """
    if context is None:
        context = {}

    # Render the template to a string asynchronously
    rendered_template = await sync_to_async(render_to_string)(template_name, context, request=request)

    # Return an HttpResponse with the rendered template
    return HttpResponse(rendered_template, status=status)
@login_required
async def quiz_view(request):
    # Fetch the team and quiz asynchronously
    team = await sync_to_async(Team.objects.get)(user=request.user)
    quiz = await sync_to_async(Quiz.objects.first)()

    # Check if the quiz is active
    if not quiz.is_active:
        return HttpResponseRedirect(reverse('team_profile'))

    # Fetch common and unique questions asynchronously
    common_questions = await sync_to_async(list)(Question.objects.filter(quiz=quiz, common_question=True))
    unique_questions = await sync_to_async(list)(Question.objects.filter(teamquestion__team=team, common_question=False))

    # Fetch submitted answers with related questions asynchronously
    submitted_answers = await sync_to_async(list)(Answer.objects.filter(team=team).select_related('question'))

    # Prepare a dictionary of answered questions
    answered_questions = {
        answer.question.id: answer.question.correct_answer for answer in submitted_answers
    }

    # Render the quiz template with the context
    return await render_async(request, 'quiz.html', {
        'common_questions': common_questions,
        'unique_questions': unique_questions,
        'answered_questions': answered_questions or {},
        'team': team
    })


@require_POST
async def submit_answer(request, question_id):
    try:
        data = json.loads(request.body)
        answer_text = data.get('answer')

        if not answer_text:
            return await json_response_async(
                {'success': False, 'error': 'Answer cannot be empty.'},
                status=400
            )

        get_question = sync_to_async(lambda: get_object_or_404(Question, id=question_id))
        question = await get_question()
        is_correct = (answer_text.strip().lower() == question.correct_answer.strip().lower())

        if is_correct:
            get_team = sync_to_async(lambda: Team.objects.get(user=request.user))
            team = await get_team()

            create_answer = sync_to_async(Answer.objects.create)
            await create_answer(
                team=team,
                question=question,
                submitted_answer=answer_text,
                is_correct=True,
                score=10 if question.common_question else 20
            )

        return await json_response_async({
            'success': True,
            'is_correct': is_correct,
        })

    except Exception as e:
        return await json_response_async(
            {'success': False, 'error': str(e)},
            status=500
        )


@login_required
async def request_hint(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        question_id = request.POST.get('question_id')

        try:
            team = await sync_to_async(Team.objects.get)(name=team_name)
            question = await sync_to_async(Question.objects.get)(id=question_id)
            await sync_to_async(HintRequest.objects.create)(team=team, question=question)
            return redirect('hint_requests')
        except Team.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Team not found.'})
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found.'})

    # Fetch user team and questions asynchronously
    user_team = await sync_to_async(Team.objects.get)(user=request.user)
    questions = await sync_to_async(list)(Question.objects.all())  # Ensure this is evaluated

    # Use render_async instead of render
    return await render_async(request, 'request_hint.html', {
        'questions': questions,
        'user_team': user_team
    })

@login_required
async def hint_requests(request):
    get_hints = sync_to_async(lambda: list(HintRequest.objects.filter(team__user=request.user)))
    hint_requests = await get_hints()
    return await render_async(request, 'hint_requests.html', {'hint_requests': hint_requests})


async def scoreboard(request):
    get_teams = sync_to_async(lambda: list(Team.objects.all()))
    get_score = sync_to_async(lambda t: Answer.objects.filter(team=t).aggregate(total=Sum('score'))['total'] or 0)
    get_hint_count = sync_to_async(lambda t: HintRequest.objects.filter(team=t).count())
    get_approved_count = sync_to_async(lambda t: HintRequest.objects.filter(team=t, is_fulfilled=True).count())
    get_answered_count = sync_to_async(lambda t: Answer.objects.filter(team=t, is_correct=True).count())

    teams = await get_teams()
    scoreboard_data = []

    for team in teams:
        total_score = await get_score(team)
        hint_requests = await get_hint_count(team)
        approved_requests = await get_approved_count(team)
        answered_questions = await get_answered_count(team)

        score_after_deduction = total_score - (approved_requests * 5)
        scoreboard_data.append({
            'team_name': team.name,
            'score': max(score_after_deduction, 0),
            'hint_requests': hint_requests,
            'approved_requests': approved_requests,
            'solved_questions': answered_questions,
        })

    scoreboard_data.sort(key=lambda x: (-x['score'], x['approved_requests']))
    return await render_async(request, 'scoreboard.html', {'scoreboard_data': scoreboard_data})

async def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

async def custom_500_view(request):
    return render(request, '500.html', status=500)

# REST APIs
class LoginView(APIView):
    async def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = await sync_to_async(authenticate)(request, username=username, password=password)
            if user is not None:
                await sync_to_async(login)(request, user)
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
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

    async def post(self, request, question_id):
        try:
            answer_text = request.data.get('answer')
            if not answer_text:
                return Response({'success': False, 'error': 'Answer cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

            question = await sync_to_async(get_object_or_404)(Question, id=question_id)
            is_correct = (answer_text.strip().lower() == question.correct_answer.strip().lower())

            if is_correct:
                team = await sync_to_async(Team.objects.get)(user=request.user)
                await sync_to_async(Answer.objects.create)(
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

    async def get(self, request):
        teams = await sync_to_async(Team.objects.all)()
        scoreboard_data = []
        for team in teams:
            total_score = await sync_to_async(Answer.objects.filter)(team=team).aggregate(total=Sum('score'))['total'] or 0
            hint_requests = await sync_to_async(HintRequest.objects.filter)(team=team).count()
            approved_requests = await sync_to_async(HintRequest.objects.filter)(team=team, is_fulfilled=True).count()
            answered_questions = await sync_to_async(Answer.objects.filter)(team=team, is_correct=True).count()
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