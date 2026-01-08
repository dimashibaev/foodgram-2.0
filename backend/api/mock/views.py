from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from access_control.models import BusinessElement, ProtectedObject
from access_control.services import get_effective_permissions


class ProtectedObjectSerializer:
    """Мини-сериализатор (ID + имя) без зависимости от ModelSerializer.

    Требование ТЗ: макет защищаемых объектов должен содержать идентификатор и имя.
    """

    @staticmethod
    def to_representation(obj: ProtectedObject) -> dict:
        return {
            'id': obj.id,
            'name': obj.name,
            'owner_id': obj.owner_id,
            'element': obj.element.code,
        }


def _get_element(element_code: str) -> BusinessElement:
    return get_object_or_404(BusinessElement, code=element_code)


def _filter_queryset(user, element: BusinessElement):
    perms = get_effective_permissions(user, element.code)
    if perms.read_all_permission:
        qs = ProtectedObject.objects.filter(element=element)
    elif perms.read_permission:
        qs = ProtectedObject.objects.filter(element=element, owner=user)
    else:
        raise PermissionDenied('Недостаточно прав на чтение')
    return qs, perms


class MockElementsIndexView(APIView):
    """Справочник доступных бизнес-элементов (защищаемых сущностей)."""

    def get(self, request):
        data = list(BusinessElement.objects.values('code', 'name').order_by('code'))
        return Response({'elements': data})


class MockElementListCreateView(APIView):
    """Работа с макетом объектов: список/создание."""

    def get(self, request, element: str):
        element_obj = _get_element(element)
        qs, _ = _filter_queryset(request.user, element_obj)
        return Response({
            'element': element_obj.code,
            'objects': [ProtectedObjectSerializer.to_representation(o) for o in qs.order_by('id')],
        })

    def post(self, request, element: str):
        element_obj = _get_element(element)
        perms = get_effective_permissions(request.user, element_obj.code)
        if not perms.create_permission:
            raise PermissionDenied('Недостаточно прав на создание')

        name = (request.data or {}).get('name', '')
        if not isinstance(name, str) or not name.strip():
            return Response({'detail': 'Поле name обязательно'}, status=status.HTTP_400_BAD_REQUEST)

        obj = ProtectedObject.objects.create(
            element=element_obj,
            owner=request.user,
            name=name.strip(),
        )
        return Response(ProtectedObjectSerializer.to_representation(obj), status=status.HTTP_201_CREATED)


class MockElementDetailView(APIView):
    """Работа с конкретным объектом: чтение/обновление/удаление."""

    def get(self, request, element: str, obj_id: int):
        element_obj = _get_element(element)
        qs, _ = _filter_queryset(request.user, element_obj)
        obj = get_object_or_404(qs, id=obj_id)
        return Response(ProtectedObjectSerializer.to_representation(obj))

    def patch(self, request, element: str, obj_id: int):
        return self._update(request, element, obj_id)

    def put(self, request, element: str, obj_id: int):
        return self._update(request, element, obj_id)

    def _update(self, request, element: str, obj_id: int):
        element_obj = _get_element(element)
        perms = get_effective_permissions(request.user, element_obj.code)

        obj = get_object_or_404(ProtectedObject, id=obj_id, element=element_obj)
        is_owner = (obj.owner_id == request.user.id)

        if perms.update_all_permission or (perms.update_permission and is_owner):
            name = (request.data or {}).get('name', '')
            if not isinstance(name, str) or not name.strip():
                return Response({'detail': 'Поле name обязательно'}, status=status.HTTP_400_BAD_REQUEST)
            obj.name = name.strip()
            obj.save(update_fields=['name'])
            return Response(ProtectedObjectSerializer.to_representation(obj))
        raise PermissionDenied('Недостаточно прав на обновление')

    def delete(self, request, element: str, obj_id: int):
        element_obj = _get_element(element)
        perms = get_effective_permissions(request.user, element_obj.code)

        obj = get_object_or_404(ProtectedObject, id=obj_id, element=element_obj)
        is_owner = (obj.owner_id == request.user.id)

        if perms.delete_all_permission or (perms.delete_permission and is_owner):
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise PermissionDenied('Недостаточно прав на удаление')
