import jwt

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Notification, Question
from core.serializers import NotificationSerializer
from utils.permission import IsOrganizer
from eon_backend.settings import SECRET_KEY

from utils.common import api_success_response, api_error_response


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsOrganizer])
def get_feedback_questions(request):
    try:
        query = Question.objects.all()
    except Exception as err:
        return api_error_response(message="Some internal error occue", status=500)
    data = []
    for question in query:
        data.append({'id': question.id, 'question': question.question})
    return api_success_response(message="Feedback questions list", status=200, data=data)