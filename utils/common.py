from rest_framework import status as http_status
from rest_framework.response import Response


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
        return Response({"message": message, "status": status}, status=status)
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
        return Response({"data": data, "status": status}, status=status)
    if message:
        return Response({"message": message, "status": status}, status=status)
    return Response(status=status)
