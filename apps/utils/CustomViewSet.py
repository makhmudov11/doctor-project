from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status


class BaseModelViewSet(ModelViewSet):

    def format_response(self, data=None, message="", success=True, status_code=status.HTTP_200_OK):
        return Response({
            "success": success,
            "message": message,
            "data": data
        }, status=status_code)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.format_response(
            data=serializer.data,
            message="Ma'lumot listi muvaffaqiyatli olindi."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.format_response(
            data=serializer.data,
            message="Ma'lumot muvaffaqiyatli olindi."
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.format_response(
            data=serializer.data,
            message="Ma'lumot muvaffaqiyatli yaratildi.",
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.format_response(
            data=serializer.data,
            message="Ma'lumot muvaffaqiyatli yangilandi."
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.format_response(
            data=None,
            message="Ma'lumot muvaffaqiyatli o'chirildi."
        )
