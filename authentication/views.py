import json

from django.db import transaction
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utils.common import api_error_response, api_success_response, default_password, produce_object_for_user
from .models import User, Role
from core.models import UserProfile


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
            message = "Given Credentials does not matches with any registered user"
            return api_error_response(message=message, status=400)
        token = get_token_for_user(user)
        token['user'] = produce_object_for_user(user)
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
        guest_login = False

        if email is None:
            return api_error_response(message='Complete details are not provided', status=400)

        # check for guest login: everything should be null except email
        if password is None:
            if role_name is None and name is None and contact_number is None and address is None and \
                    organization is None:
                # guest login
                guest_login = True
            else:
                return api_error_response(message='Incomplete or Incorrect Credentials are provided for registration',
                                          status=400)
        else:
            # for every other case except Guest login, role_name is mandatory field
            if role_name is None:
                return api_error_response(message='Incomplete or Incorrect Credentials are provided for registration',
                                          status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # if user is None then new_user will be created
            user = None
        if guest_login:
            # checking if a user already exist or not
            # guest registration
            guest_login = False
            try:
                if user is not None:
                    return api_error_response(message='A user already exist with the given email id: {}'.format(email),
                                              status=400)
                else:
                    user = User.objects.create_user(email=email, password=default_password)
                    user_details_obj = UserProfile.objects.create(user=user)
                    user_details_obj.save()

                    token = get_token_for_user(user)
                    token['user_id'] = user.id
                    return api_success_response(data=token, message='Guest User created successfully', status=201)

            except Exception as err:
                return api_error_response(message=str(err), status=400)

        else:
            try:
                try:
                    # Checking if role is correct or not
                    role_name = role_name.lower()
                    role_obj = Role.objects.get(role=role_name)
                except Role.DoesNotExist:
                    return api_error_response(message='Role assigned is not matching with any role type', status=400)
                if user is not None:
                    # check if a guest user exist with same email, if exist then update the details and return
                    user_details_object = UserProfile.objects.get(user=user)
                    user_is_guest = user_details_object.role.role == 'guest'
                    if user_is_guest:
                        # set new details to the already existed user object
                        user.set_password(password)
                        user.save()
                        UserProfile.objects.filter(user=user).update(name=name, contact_number=contact_number,
                                                                    organization=organization, address=address,
                                                                    role=role_obj)
                    else:
                        return api_error_response(message='A user already exist with the given email id: {}'.
                                                  format(email), status=400)

                else:
                    user = User.objects.create_user(email=email, password=password)

                    user_profile_obj = UserProfile.objects.create(user=user, name=name, contact_number=contact_number,
                                                                 organization=organization, address=address,
                                                                 role=role_obj)
                    user_profile_obj.save()

                token = get_token_for_user(user)
                token['user'] = produce_object_for_user(user)
                return api_success_response(data=token, message='User created successfully', status=201)
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
    try:
        if email is None or password is None:
            return api_error_response(message='Email_id and password must be provided')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return api_success_response(message='Password updated successfully')
    except Exception as err:
        return api_error_response(message=str(err))
