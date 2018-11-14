from rest_framework.permissions import BasePermission
from .models import Booking, KartUser
from django.contrib.auth.models import User

class IsOwner(BasePermission):
    """Custom permission class to allow only Booking or KartUser instances owners to edit them."""
    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the Booking, KartUser or User owner."""
        if isinstance(obj, Booking):
            return str(obj.owner) == str(request.user)
        if isinstance(obj,KartUser):
            return obj.name==str(request.user)
        if isinstance(obj,User):
            return obj.email==str(request.user)
        return obj.owner == request.user