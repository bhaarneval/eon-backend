import json
import jwt

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Question, UserProfile, UserFeedback, Feedback, Event
from core.serializers import FeedBackSerializer
from utils.permission import IsOrganizer, IsSubscriberOrReadOnly
from eon_backend.settings import SECRET_KEY

from utils.common import api_success_response, api_error_response


class FeedbackView(APIView):
    """
    API for feedback
    """
    serializer_class = FeedBackSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        API to post feedback
        :param request: body will contain event_id and answer to all the questions in provided format
        :return: success response
        """
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        if not UserProfile.objects.get(user=request.user).role.role == 'subscriber':
            return api_error_response(message="You do not have permission to perform this action.", status=403)

        data = json.loads(request.body)
        event_id = data['event_id']
        feedback = data['feedback']

        try:
            user_feedback = UserFeedback.objects.get(user_id=user_id, event_id=event_id)
        except UserFeedback.DoesNotExist:
            user_feedback = UserFeedback.objects.create(user_id=user_id, event_id=event_id)

        for response in feedback:
            question_id = response.get("question_id", None)
            if not question_id:
                return api_error_response(message="You must provide question id for all questions", status=400)
            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return api_error_response(message="Question Ids are not correct", status=400)

            answer_description = response['answer']['description']
            image = response.get('answer').get('image')
            try:
                feedback_obj = Feedback.objects.create(user_feedback=user_feedback, question=question,
                                                       answer=answer_description, image=image)
            except Exception as err:
                return api_error_response(message="Some internal error occur", status=500)
        return api_success_response(message="Successfully submitted", status=200)

    def get(self, request):
        """
        API to get the list of all feedback for an event
        :param request: in params pass event_id=<event_id>
        :return: Feedback list if success
        """
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']

        if UserProfile.objects.get(user=request.user).role.role == 'subscriber':
            return api_error_response(message="You do not have permission to perform this action.", status=403)
        event_id = request.GET.get("event_id", None)
        if not event_id:
            return api_error_response(message="You have to provide event_id in feedback details", status=400)
        event_id = int(event_id)
        try:
            event = Event.objects.get(id=event_id)
        except Exception:
            return api_error_response(message="Provided event doesn't exist", status=400)

        if event.event_created_by != request.user:
            return api_error_response(message="You can only see feedback for self organized events", status=400)

        user_feedback = UserFeedback.objects.filter(event_id=event_id)
        data = []
        for instance in user_feedback:
            feedback = Feedback.objects.filter(user_feedback=instance)
            current_response = {'user': {
                'id': instance.user.id,
                'email': instance.user.email,
                'contact': UserProfile.objects.get(user_id=instance.user.id).contact_number
            },
                'responses': []}
            for response in feedback:
                current_response['responses'].append({
                    'question_id': response.question.id,
                    'question': response.question.question,
                    'answer': response.answer,
                    'image': "https://s3.ap-south-1.amazonaws.com/backend-bucket-bits-pilani/" + response.image
                })
            data.append(current_response)
        return api_success_response(message="All feedback", status=200, data=data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsOrganizer])
def get_feedback_questions(request):
    """
    API to get all questions assigned for feedback
    :return: questions for feedback
    """
    try:
        query = Question.objects.all()
    except Exception as err:
        return api_error_response(message="Some internal error occue", status=500)
    data = []
    for question in query:
        data.append({'id': question.id, 'question': question.question})
    return api_success_response(message="Feedback questions list", status=200, data=data)
