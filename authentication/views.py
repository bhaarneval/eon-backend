import json

from django.db import transaction
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from rest_framework.decorators import api_view
from utils.common import api_error_response, api_success_response
from .models import User, Role, UserDetails


class Login(APIView):
    """API for login"""

    def post(self, request):
        """
            :param request: Header containing JWT and secret for User
            'HTTP_AUTHORIZATION':param request: email : user's email id for logging in
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
            message = "Given Credentials does not matches with any registered user"
            return api_error_response(message=message, status=400)
        token = get_token_for_user(user)
        token['user_id'] = user.id
        return api_success_response(data=token)


class Register(APIView):

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

        if email is None or password is None or contact_number is None or organization is None:
            return api_error_response(message='Complete details are not provided', status=400)

        try:
            # Checking if new_role is created or not
            if role_name is not None:
                try:
                    role_obj = Role.objects.get(role=role_name)
                except Role.DoesNotExist:
                    return api_error_response(message='Role assigned is not matching with any role type', status=400)
            try:
                user = User.objects.get(email=email)
                if user is not None:
                    return api_error_response(message='A user already exist with the given email id: {}'.format(email),
                                              status=400)
            except User.DoesNotExist:
                user = User.objects.create_user(email=email, password=password)
            user_details_obj = UserDetails.objects.create(user=user, name=name, contact_number=contact_number,
                                                          organization=organization, address=address, role=role_obj)
            user_details_obj.save()

            token = get_token_for_user(user)
            token['user_id'] = user.id

            return api_success_response(data=token, message='User created successfully', status=201)
        except Exception as err:
            return api_error_response(message=str(err), status=400)


class change_user_password(APIView):
    def post(self, request):
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
            message = "Given Credentials does not matches with any registered user"
            return api_error_response(message=message, status=400)

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
