import json
import logging

from django.db.models import Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from asgiref.sync import sync_to_async

from .forms import  RegistrationForm
from .models import Team, Quiz, Question, HintRequest, Answer, TeamUser, Hint, HintNotification, UserPerson, \
    SiteSettings
from .serializers import TeamSerializer, QuizSerializer, QuestionSerializer, HintRequestSerializer, AnswerSerializer, \
    TeamUser, HintNotificationSerializer, HintSerializer, TeamUserSerializer, LoginSerializer

Serializer, HintSerializer, HintNotificationSerializer, LoginSerializer

# Web Views
json_response_async = sync_to_async(JsonResponse)

async_render = sync_to_async(TemplateResponse)
async_redirect = sync_to_async(redirect)

async def reg_error(request):
    return render(request, 'reg.html')


def login_view(request):
    if request.method == 'POST':
        team_name = request.POST['team_name']
        password = request.POST['password']

        try:
            team = Team.objects.get(name=team_name)

            if team.check_password(password):
                request.session['team_id'] = team.id
                return redirect('team_profile')
        except Team.DoesNotExist:
            pass

        return HttpResponse("Invalid team name or password")

    return render(request, 'login.html')


@login_required
async def team_profile(request):
    # Get the team ID from the session
    team_id = request.session.get('team_id')

    # Fetch the team asynchronously using the team ID
    team = await sync_to_async(Team.objects.get)(id=team_id)

    # Fetch the quiz asynchronously
    quiz = await sync_to_async(Quiz.objects.first)()

    # Fetch team users asynchronously
    team_users = await sync_to_async(list)(TeamUser.objects.filter(team=team))

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
    # Get the team ID from the session
    team_id = request.session.get('team_id')

    # Fetch the team asynchronously using the team ID
    team = await sync_to_async(Team.objects.get)(id=team_id)

    # Fetch the quiz asynchronously
    quiz = await sync_to_async(Quiz.objects.first)()

    # Check if the quiz is active
    if not quiz.is_active:
        return HttpResponseRedirect(reverse('team_profile'))

    # Fetch common and unique questions asynchronously
    common_questions = await sync_to_async(list)(Question.objects.filter(quiz=quiz, common_question=True))
    unique_questions = await sync_to_async(list)(
        Question.objects.filter(teamquestion__team=team, common_question=False))

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
            get_team = sync_to_async(lambda: Team.objects.get(id=request.session.get('team_id')))
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
        question_id = request.POST.get('question_id')

        # Get the team ID from the session
        team_id = request.session.get('team_id')

        try:
            # Fetch the team and question asynchronously
            team = await sync_to_async(Team.objects.get)(id=team_id)
            question = await sync_to_async(Question.objects.get)(id=question_id)

            # Create a new hint request
            await sync_to_async(HintRequest.objects.create)(team=team, question=question)
            return redirect('hint_requests')
        except Team.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Team not found.'})
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found.'})

    # Fetch user team and questions asynchronously
    team_id = request.session.get('team_id')
    user_team = await sync_to_async(Team.objects.get)(id=team_id)
    questions = await sync_to_async(list)(Question.objects.all())  # Ensure this is evaluated

    # Use render_async instead of render
    return await render_async(request, 'request_hint.html', {
        'questions': questions,
        'user_team': user_team
    })
@login_required
async def hint_requests(request):
    # Get the team ID from the session
    team_id = request.session.get('team_id')

    # Fetch the hint requests associated with the team asynchronously
    get_hints = sync_to_async(lambda: list(HintRequest.objects.filter(team_id=team_id)))
    hint_requests = await get_hints()

    return await render_async(request, 'hint_requests.html', {'hint_requests': hint_requests})


async def scoreboard(request):
    # Fetch all teams asynchronously
    teams = await sync_to_async(list)(Team.objects.all())

    scoreboard_data = []

    for team in teams:
        # Fetch scores, hint counts, and answered questions asynchronously
        total_score = await sync_to_async(
            lambda t: Answer.objects.filter(team=t).aggregate(total=Sum('score'))['total'] or 0
        )(team)

        hint_requests = await sync_to_async(
            lambda t: HintRequest.objects.filter(team=t).count()
        )(team)

        approved_requests = await sync_to_async(
            lambda t: HintRequest.objects.filter(team=t, is_fulfilled=True).count()
        )(team)

        answered_questions = await sync_to_async(
            lambda t: Answer.objects.filter(team=t, is_correct=True).count()
        )(team)

        # Calculate score after deduction
        score_after_deduction = total_score - (approved_requests * 5)

        scoreboard_data.append({
            'team_name': team.name,
            'score': max(score_after_deduction, 0),
            'hint_requests': hint_requests,
            'approved_requests': approved_requests,
            'solved_questions': answered_questions,
        })

    # Sort the scoreboard data by score and approved requests
    scoreboard_data.sort(key=lambda x: (-x['score'], x['approved_requests']))

    # Render the scoreboard template with the data
    return await render_async(request, 'scoreboard.html', {'scoreboard_data': scoreboard_data})

async def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

async def custom_500_view(request):
    return render(request, '500.html', status=500)


@require_http_methods(["GET"])
async def home(request):
    settings = await sync_to_async(get_site_settings)()

    return render(request, 'home1.html', {
        'registration_open': settings.registration_open,
        'login_open': settings.login_open
    })


def get_site_settings():
    try:
        return SiteSettings.objects.first()  # Use .first() instead of .afirst()
    except SiteSettings.DoesNotExist:
        # Create default settings if not exist
        return SiteSettings.objects.create(
            registration_open=True,
            login_open=True
        )
@sync_to_async
def validate_form(post_data):
    form = RegistrationForm(post_data)
    return form, form.is_valid()

@sync_to_async
def save_user_form(form):
    user = form.save(commit=False)
    user.set_password(form.cleaned_data['password'])
    user.save()

@sync_to_async
def get_blank_form():
    return RegistrationForm()


@require_http_methods(["GET", "POST"])
async def register(request):
    # Check site settings asynchronously
    settings = await sync_to_async(SiteSettings.objects.first)()
    if not settings or not settings.registration_open:
        return await sync_to_async(render)(request, 'registration_closed.html', {})

    if request.method == 'POST':
        # Handle form submission asynchronously
        form = RegistrationForm(request.POST)
        is_valid = await sync_to_async(form.is_valid)()  # Validate form asynchronously
        print("Form is valid:", is_valid)  # Debugging
        if not is_valid:
            print("Form errors:", form.errors)  # Debugging
        if is_valid:
            user = await sync_to_async(form.save)()  # Save the user asynchronously
            print("User saved:", user)  # Debugging
            return redirect('done')  # Redirect to a success page
    else:
        form = RegistrationForm()  # Display a blank form

    context = {'form': form}
    return await sync_to_async(render)(request, 'register.html', context)
logger = logging.getLogger(__name__)

def user_login_view(request):
    error_message = None

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        logger.info(f"Attempting login for email: {email}")

        try:
            user = UserPerson.objects.get(email=email)
            logger.info(f"User found: {user.email}")

            if user.check_password(password):
                # Save email in session
                request.session['email'] = user.email
                request.session.save()
                logger.info("Login successful, redirecting to profile")
                return redirect('user_profile')
            else:
                logger.warning("Invalid password")
                error_message = "Invalid email or password"
        except UserPerson.DoesNotExist:
            logger.warning("User not found")
            error_message = "Invalid email or password"

    # Render the login template with the error message (if any)
    return render(request, 'user_login.html', {'error_message': error_message})
async def user_profile(request):
    # Get email from session (using sync_to_async)
    email = await sync_to_async(request.session.get)('email')
    if not email:
        logger.warning("No email in session, redirecting to login")
        return redirect('user_login')

    try:
        # Fetch user asynchronously
        user = await sync_to_async(UserPerson.objects.get)(email=email)
        logger.info(f"Rendering profile for user: {user.email}")
        return render(request, 'profile.html', {'user': user})
    except UserPerson.DoesNotExist:
        logger.warning("User  not found")
        return redirect('user_login')
async def done(request):
    return render(request, 'done.html')

# REST APIs
class LoginView(APIView):
    async def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            team_name = serializer.validated_data['username']  # Assuming username is the team name
            password = serializer.validated_data['password']
            # Authenticate using the Team model
            team = await sync_to_async(Team.objects.get)(name=team_name)

            if team.check_password(password):
                request.session['team_id'] = team.id  # Store team ID in session
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