from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import exception_handler

from core.exceptions import CoreAppException


def api_exception_handler(exception, context):
    """
    Custom exception handler for API's
    :param exc:
    :param context:
    :return:
    """
    if isinstance(exception, CoreAppException):
        response = Response(
            dict(
                errorCode=exception.default_code, errorMessage=exception.default_detail
            ),
            status=exception.status_code,
        )
    elif isinstance(exception, ValidationError) and "unique" in list(
        exception.get_full_details().values()
    )[0][0].get("code"):
        response = Response(
            dict(
                errorMessage=list(exception.get_full_details().values())[0][0].get(
                    "message"
                ),
                errorDetail=exception.__dict__,
            ),
            status=400,
        )
    elif isinstance(exception, ValidationError) and "unique" not in list(exception.get_full_details().values())[0][0].get("code"):
        error_details = exception.__dict__
        error_details = error_details['detail']
        response = Response(
            dict(
                errorMessage="Request Parameters are invalid",
                errorDetail=error_details,
            ),
            status=400,
        )
    else:
        response = exception_handler(exception, context)
    return response
