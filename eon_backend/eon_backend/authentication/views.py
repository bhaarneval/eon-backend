from rest_framework.generics import GenericAPIView


class Login(GenericAPIView):
    """
    API for login
    """

    def post(self, request):
        """
        :param request: Email ID and Password for user login   
        :return: json containing access and refresh token for success in authentication 
        """
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        return api_success_response(data=token)

        # if email is None or password is None:
        #     message = "EmailId & Password must be provided"
        #     return api_error_response(message=message)
        # 
        # try:
        #     email_exist = User.objects.get(email=email)
        # except Exception as err:
        #     message = "Not Registered"
        #     return api_error_response(message=message)
        # 
        # try:
        #     user = authenticate(email=email, password=password)
        # except Exception as err: 
        #     message = "invalid password"
        #     return api_error_response(message=message)