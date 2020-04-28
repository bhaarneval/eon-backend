"""
Authentications view reference are here
"""
import json
from random import randint

from django.db import transaction
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from eon_backend.settings.common import ADMIN_EMAIL
from utils.common import api_error_response, api_success_response, \
    produce_object_for_user
from utils.helper import send_email_sms_and_notification
from core.models import UserProfile
from .models import User, Role, VerificationCode


class Login(APIView):
    """API for login"""

    def post(self, request):
        """
            :param request: email : user's email id for logging in
            :param request: password : user's password for logging in
            :return: json containing access and refresh token if the user is authenticated
        """
        data = json.loads(request.body)
        email = data.get('email', None)
        password = data.get('password', None)

        try:
            user = authenticate(username=email, password=password)
        except Exception as err:
            return api_error_response(message=str(err), status=400)

        if user is None:
            message = "Given credentials do not match with any registered user"
            return api_error_response(message=message, status=400)
        token = get_token_for_user(user)
        user_obj = produce_object_for_user(user)
        if user_obj is None:
            return api_error_response(
                message='Some error is coming in returning response', status=400)
        token['user'] = user_obj
        return api_success_response(data=token)


class Register(APIView):
    """
    Api for Registration
    """

    @transaction.atomic()
    def post(self, request):
        """
            :param request: email : user's emailId for logging in
            :param request: password : user's password for logging in
            :return: api success response if registration is successful
        """
        data = json.loads(request.body)
        email = data.get('email')
        name = data.get('name')
        contact_number = data.get('contact')
        address = data.get('address')
        password = data.get('password')
        organization = data.get('organization')
        role_name = data.get('role')

        if email is None or password is None or role_name is None:
            return api_error_response(
                message='Incomplete or incorrect credentials are provided for registration',
                status=400)

        try:
            # Checking if role is correct or not
            role_name = role_name.lower()
            role_obj = Role.objects.get(role=role_name)
        except Role.DoesNotExist:
            return api_error_response(
                message='Role assigned is not matching with any role type', status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # if user is None then new_user will be created
            user = None

        if user is not None:
            return api_error_response(message='A user already exist with the given email id: {}'.
                                      format(email), status=400)

        try:
            user = User.objects.create_user(email=email, password=password)

            user_profile_obj = UserProfile.objects.create(
                user=user, name=name, contact_number=contact_number,
                organization=organization, address=address,
                role=role_obj)
            user_profile_obj.save()
            if role_name == 'organizer':
                user.is_active = False
                user.save()
                token = {}
                send_email_sms_and_notification(action_name="new_organiser_created",
                                                email_ids=[ADMIN_EMAIL],
                                                user_email=email)
            else:
                token = get_token_for_user(user)

            token['user'] = produce_object_for_user(user)
            return api_success_response(data=token,
                                        message='User created successfully', status=201)
        except Exception as err:
            return api_error_response(message=str(err), status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def change_user_password(request):
    """
        Function to set current user's password
        :param request: password: password to be reset
                        email: emailId as a username
        :return: JSON confirming password was changed or not
    """

    data = json.loads(request.body)
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if email is None or old_password is None or new_password is None:
        return api_error_response(message='No field can be left blank')
    try:
        user = authenticate(username=email, password=old_password)
    except Exception as err:
        return api_error_response(message=str(err), status=400)

    if user is None:
        message = "Given credentials does not matches with any registered user"
        return api_error_response(message=message, status=400)

    if old_password == new_password:
        return api_error_response(message="New password cannot be same as old password", status=400)

    try:
        user.set_password(new_password)
        user.save()
        return api_success_response(message='Password updated successfully')
    except Exception as err:
        return api_error_response(message=str(err))


def get_token_for_user(user):
    """
    :param user: user for which token is generated
    :return: {
        access_token: <value>
        refresh_token: <value>
    }
    """
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
def reset_password(request):
    """
    API for forgot password, will be called after sms integration
    :param request: email and password as {"email": <email_id> , "password": "password"}
    :return: Success if password is changed
    """
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    code = data.get('code')
    try:
        code_obj = VerificationCode.objects.get(email=email, is_active=True)
        try:
            user_existed = authenticate(username=email, password=password)
        except Exception:
            return api_error_response(message="Some internal error occur", status=500)
        if user_existed:
            return api_error_response(message="New password cannot be same as old password")
        if code_obj and code_obj.code == code:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            code_obj.is_active = False
            code_obj.save()
            return api_success_response(message='Password updated successfully')
        return api_error_response(message="Invalid Code", status=400)
    except Exception as err:
        return api_error_response(message=str(err), status=500)


@api_view(['POST'])
def send_forget_password_mail(request):
    """
        API for sending verification code on the giving mail
        :param request: email
        :return: Success if mail send
    """
    data = json.loads(request.body)
    email = data.get('email')
    try:
        User.objects.get(email=email)
    except User.DoesNotExist:
        return api_error_response(message="Please provide the registered email id.", status=400)
    verification_code = randint(1000, 9999)
    VerificationCode.objects.filter(email=email, is_active=True).update(is_active=False)
    code = VerificationCode(email=email, code=verification_code)
    code.save()
    send_email_sms_and_notification(
        action_name="forget_password",
        verification_code=verification_code,
        email_ids=[email]
    )
    return api_success_response(message="Verification code send successfully")
