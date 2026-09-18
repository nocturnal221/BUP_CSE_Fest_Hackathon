from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {"error": "An internal error occurred during optimization."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return response
