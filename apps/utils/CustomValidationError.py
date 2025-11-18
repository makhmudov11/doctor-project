from rest_framework.exceptions import APIException
from rest_framework import status


class CustomValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Xato yuz berdi"
    default_code = "custom_error"

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = {"success": False, "message": detail, "data": None}
        else:
            self.detail = {"success": False, "message": self.default_detail, "data": None}
