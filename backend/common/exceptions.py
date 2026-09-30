from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        # Never serialize the exception, request body, DB credentials or traceback.
        return Response(
            {"detail": "No se pudo completar la operación. Inténtalo nuevamente."}, status=500
        )
    return response
