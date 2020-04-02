from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User, Status, Role, UserDetails


class Login(APIView):
    """
        API for login
    """

    def post(self, request):
        """

            :param request: Header containing JWT and secret for User
            'HTTP_AUTHORIZATION':param request: email : user's emailId for logging in
            :param request: password : user's password for logging in
            :return: json containing access and refresh token if the user is authenticated
        """
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        user = authenticate(username=email, password=password)

        if user is None:
            return Response(data={"User with the given credentials does not exist"}, status=400)
        token = self.get_token_for_user(user)
        token['user_id'] = user.id
        return Response(data=token)

    def get_token_for_user(self, user):
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


class Register(APIView):

    def post(self, request):
        """
            :param request: email : user's emailId for logging in
            :param request: password : user's password for logging in
            :return: api success response if registration is successful
        """
        email = request.POST.get('email')
        name = request.POST.get('name')
        contact_number = request.POST.get('contact')
        address = request.POST.get('address')
        password = request.POST.get('password')
        organization = request.POST.get('organization')
        role_name = request.POST.get('role')
        status = request.POST.get('status')

        if email is None or password is None or contact_number is None or organization is None:
            return Response(data='Complete details are not provided', status_code=400)

        try:
            role_obj = None
            status_obj = None
            # Checking if new_role is created or not
            if role_name is not None:
                role_obj = Role.objects.get(role=role_name)
                if role_obj is None:
                    role_obj = Role.objects.create(role=role_name)

            # Checking if new_role is created or not
            if status is not None:
                status_obj = Status.objects.get(status=status)
                if status_obj is None:
                    status_obj = Status.objects.create(status=status)

            user = User.objects.create_user(email=email, password=password)
            user_details_obj = UserDetails.objects.create(user=user, name=name, contact_number=contact_number,
                                                          organization=organization, address=address, status=status_obj,
                                                          role=role_obj)
            user_details_obj.save()

            return Response(data='User created successfully', status=201)
        except Exception as err:
            return Response(data=str(err))


