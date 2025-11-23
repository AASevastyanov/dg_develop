from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from django.contrib.auth import get_user_model
User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
