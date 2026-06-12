from rest_framework.permissions import BasePermission


class IsGuard(BasePermission):
    """Allows access only to verified, active guards."""

    message = "Only active verified guards can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "guard_profile")
            and request.user.guard_profile.verification_status == "ACTIVE"
        )


class IsVerifiedUser(BasePermission):
    """Allows access only to active (non-suspended, non-deleted) users."""

    message = "Your account is suspended or inactive."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and not request.user.is_suspended
            and not request.user.is_deleted
        )


class IsBookingParticipant(BasePermission):
    """Allows access only if the user is the booking's client or assigned guard."""

    message = "You are not a participant in this booking."

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_client = obj.user == user
        is_guard = (
            hasattr(user, "guard_profile")
            and obj.guard is not None
            and obj.guard == user.guard_profile
        )
        return is_client or is_guard


class IsAdminUser(BasePermission):
    """Restricts access to platform staff/admin only."""

    message = "Only platform administrators can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsGuardOrUser(BasePermission):
    """Allows access to any authenticated, non-suspended user or guard."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and not request.user.is_suspended
        )


class IsOwner(BasePermission):
    """Generic owner check — object must have a `user` field."""

    message = "You do not own this resource."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
