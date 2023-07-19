from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        print("Input permission", request.user, obj.owner)
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
       

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user
