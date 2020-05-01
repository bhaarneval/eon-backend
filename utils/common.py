"""
Common methods are here
"""
import datetime

import jwt
from rest_framework import status as http_status
from rest_framework.response import Response

from eon_backend.settings import DECODE_KEY


def api_error_response(message, status=None):
    """
    returns an error message if there is an error in GET API
    :param message: error message from request
    :type message: str
    :param status: status of the request
    :return: returns the message and status
    """
    if not status:
        status = http_status.HTTP_400_BAD_REQUEST

    if isinstance(message, str):
        return Response({"message": message}, status=status)
    return Response(message, status=status)


def api_success_response(message=None, data=None, status=None):
    """
    returns a success response whenever API is hit successfully
    :param message: message to indicate the status of response
    :type message: str
    :param data:data of the fields
    :type data: list or dict
    :param status: status
    :return: returns the status of the successful response
    """
    if not status:
        status = http_status.HTTP_200_OK

    if data is not None and isinstance(data, list) or isinstance(data, dict):
        if message:
            return Response({"data": data, "message": message}, status=status)

        return Response({"data": data}, status=status)
    if message:
        return Response({"message": message}, status=status)
    return Response(status=status)


default_password = 'default'


def produce_object_for_user(user):
    """
    Function to produce object for user_Details
    :param user: user object
    :return: An Object with complete details
    """
    from core.models import UserProfile
    try:
        user_profile = UserProfile.objects.get(user=user.id)
    except UserProfile.DoesNotExist:
        return None
    response = {'user_id': user.id, 'email': user.email, 'active_status': user.is_active,
                'name': user_profile.name, 'created_on': user_profile.created_on,
                'updated_on': user_profile.updated_on,
                'contact_number': user_profile.contact_number,
                'organization': user_profile.organization,
                'address': user_profile.address,
                'role': {'id': user_profile.role.id, 'role': user_profile.role.role}}
    return response


def payment_token(user_id):
    payload = {'user_id': user_id}
    encoded_jwt = jwt.encode(payload, "THISISVERYSECRETKEY", algorithm="HS256")
    return encoded_jwt
