from rest_framework import generics, permissions, views, viewsets, mixins
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.auth import get_user_model
from .permissions import IsOrganizationOwner
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from users.serializers import UserUpdateSerializer, UserSerializer
from organizations.models import Organization, Course, Enrollment
from organizations.serializers import OrganizationSerializer, CourseSerializer, EnrollmentSerializer
from events.models import Event
from events.serializers import EventSerializer
from exams.models import Exam, Result
from exams.serializers import ExamSerializer, ResultSerializer, ExamCreateSerializer, SubmitExamSerializer
from drf_yasg.utils import swagger_auto_schema

PERCENT_TO_PASS_EXAM = 60

User = get_user_model()


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer


class OrganizationAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(response_body=OrganizationSerializer)
    def get(self, request, pk=None):
        organization = get_object_or_404(Organization, pk=pk)
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)


class OrganizationCreateRetrieveUpdateAPIView(mixins.CreateModelMixin,
                                              mixins.RetrieveModelMixin,
                                              mixins.UpdateModelMixin,
                                              generics.GenericAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationOwner]

    def get_object(self):
        return get_object_or_404(Organization, owner=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class OrganizationListAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)


class CourseListAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'organization':
            # Для организаций показываем только их курсы
            organization = request.user.organizations.first()
            if organization:
                courses = Course.objects.filter(organization=organization)
            else:
                courses = Course.objects.none()
        else:
            # Для обычных пользователей показываем все курсы
            courses = Course.objects.all()
        
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class CourseCreateAPIView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationOwner]


class CourseDetailAPIView(views.APIView):
    @swagger_auto_schema(request_body=CourseSerializer, responses={200: CourseSerializer, 400: 'Bad Request', 404: 'Course not found'})
    def patch(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(data=request.data,
                                      context={'request': request},
                                      instance=course,
                                      partial=True)
        if serializer.is_valid():
            course = serializer.save()
            return Response(CourseSerializer(course).data, status=200)
        return Response(serializer.errors, status=400)
    
    @swagger_auto_schema(responses={200: CourseSerializer, 404: 'Course not found'})
    def get(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
    def delete(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        # Проверяем, что пользователь является владельцем организации, которой принадлежит курс
        if request.user.role != 'organization' or course.organization.owner != request.user:
            return Response({'error': 'У вас нет прав для удаления этого курса'}, status=403)
        course.delete()
        return Response({'message': 'Курс успешно удален'}, status=204)
        
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsOrganizationOwner()]
        return [permissions.IsAuthenticated()]


class EventViewSet(ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all().order_by('level')
    serializer_class = ExamSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Exam.objects.none()
        if self.request.user.role == 'organization':
            return self.queryset.filter(author=self.request.user.organizations.first())
        return self.queryset
    
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return ExamCreateSerializer
        return ExamSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return [permissions.IsAuthenticated(), IsOrganizationOwner()]
        return [permissions.IsAuthenticated()]


@swagger_auto_schema(request_body=SubmitExamSerializer, methods=['post'])
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_exam(request):
    exam_id = request.data.get('exam_id')
    answers = request.data.get('answers', [])

    if not exam_id or not answers:
        return Response({'error': 'exam_id и answers обязательны'}, status=400)

    exam = get_object_or_404(Exam, id=exam_id)
    score = 0
    right_answers = 0
    for answer in answers:
        question_number = answer['question_number']
        text = answer['text']
        if not question_number or not text:
            continue

        question = exam.questions.filter(number=question_number).first()
        if not question:
            continue

        selected_choice = question.choices.filter(text=text).first()
        if selected_choice and selected_choice.is_correct:
            score += question.point
            right_answers += 1

    result_percent = score / exam.total_points * 100
    passed = result_percent >= PERCENT_TO_PASS_EXAM

    if passed:
        result = Result.objects.filter(user=request.user, exam=exam).first()
        if result:
            if result.score < score:
                result.score = score
                result.save()
        result = Result.objects.create(user=request.user, exam=exam, score=score)
    return Response({
        'result': 'passed' if passed else 'failed',
        'score': score,
        'percent': result_percent,
        'right_answers': right_answers
    }, status=200)


class ResultRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Result.objects.none()
        user = self.request.user
        return Result.objects.filter(user=user)
    
    def get_object(self):  
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        return obj


class ResultListAPIView(generics.ListAPIView):
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Result.objects.filter(user=user).order_by('-completed_at')


class EnrollmentViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)


# Celery task views
from celery.result import AsyncResult
from api.tasks import fetch_weather_task, fetch_news_task


@swagger_auto_schema(methods=['post'], request_body=None)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_weather_task(request):
    """
    Trigger weather API task.
    
    Expected body:
    {
        "city": "Kazan",
        "country": "RU"
    }
    """
    city = request.data.get('city', 'Kazan')
    country = request.data.get('country', 'RU')
    
    task = fetch_weather_task.delay(city, country)
    
    return Response({
        'task_id': task.id,
        'status': 'PENDING',
        'message': 'Weather task has been queued'
    }, status=202)


@swagger_auto_schema(methods=['post'], request_body=None)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_news_task(request):
    """
    Trigger news API task.
    
    Expected body:
    {
        "query": "technology",
        "language": "en"
    }
    """
    query = request.data.get('query', 'technology')
    language = request.data.get('language', 'en')
    
    task = fetch_news_task.delay(query, language)
    
    return Response({
        'task_id': task.id,
        'status': 'PENDING',
        'message': 'News task has been queued'
    }, status=202)


@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_task_status(request, task_id):
    """
    Get status of a Celery task.
    
    Returns task state and result if available.
    """
    task_result = AsyncResult(task_id)
    
    response_data = {
        'task_id': task_id,
        'state': task_result.state,
    }
    
    if task_result.state == 'PENDING':
        response_data['message'] = 'Task is waiting to be processed'
    elif task_result.state == 'PROGRESS':
        response_data['current'] = task_result.info.get('current', 0)
        response_data['total'] = task_result.info.get('total', 1)
    elif task_result.state == 'SUCCESS':
        response_data['result'] = task_result.result
    elif task_result.state == 'FAILURE':
        response_data['error'] = str(task_result.info)
    
    return Response(response_data, status=200)
