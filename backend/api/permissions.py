from rest_framework import permissions

class IsOrganizationOwner(permissions.BasePermission):
    """
    Custom permission to only allow organization owners to access certain views.
    """

    def has_permission(self, request, view):
        # Allow access if the user is authenticated and is an organization owner
        return request.user.role == 'organization' or request.method in permissions.SAFE_METHODS
    def has_object_permission(self, request, view, obj):
        # Allow access if the user is the owner of the organization
        return obj.author == request.user.organizations.first() or request.method in permissions.SAFE_METHODS