from django.db import transaction
from apps.users.models import UserProfile, Address, EmergencyContact
from rest_framework.exceptions import ValidationError as ServiceValidationError


class UserService:
    @staticmethod
    def update_profile(user: UserProfile, validated_data: dict) -> UserProfile:
        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()
        return user

    @staticmethod
    def update_fcm_token(user: UserProfile, fcm_token: str) -> None:
        user.fcm_token = fcm_token
        user.save(update_fields=["fcm_token"])

    @staticmethod
    def request_account_deletion(user: UserProfile) -> None:
        import django.utils.timezone as tz

        user.is_deleted = True
        user.deleted_at = tz.now()
        user.is_active = False
        user.save(update_fields=["is_deleted", "deleted_at", "is_active"])

    # ---------- Addresses ----------

    @staticmethod
    def list_addresses(user: UserProfile):
        return Address.objects.filter(user=user).order_by("-is_default", "created_at")

    @staticmethod
    def create_address(user: UserProfile, validated_data: dict) -> Address:
        count = Address.objects.filter(user=user).count()
        if count >= 10:
            raise ServiceValidationError("Maximum of 10 saved addresses allowed.")
        validated_data["user"] = user
        with transaction.atomic():
            address = Address(**validated_data)
            address.save()
        return address

    @staticmethod
    def update_address(user: UserProfile, address_id, validated_data: dict) -> Address:
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Address not found.")
        for attr, value in validated_data.items():
            setattr(address, attr, value)
        address.save()
        return address

    @staticmethod
    def delete_address(user: UserProfile, address_id) -> None:
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Address not found.")
        address.delete()

    # ---------- Emergency Contacts ----------

    @staticmethod
    def list_emergency_contacts(user: UserProfile):
        return EmergencyContact.objects.filter(user=user).order_by(
            "-is_primary", "created_at"
        )

    @staticmethod
    def create_emergency_contact(
        user: UserProfile, validated_data: dict
    ) -> EmergencyContact:
        count = EmergencyContact.objects.filter(user=user).count()
        if count >= 5:
            raise ServiceValidationError("Maximum of 5 emergency contacts allowed.")
        validated_data["user"] = user
        contact = EmergencyContact(**validated_data)
        contact.save()
        return contact

    @staticmethod
    def update_emergency_contact(
        user: UserProfile, contact_id, validated_data: dict
    ) -> EmergencyContact:
        try:
            contact = EmergencyContact.objects.get(id=contact_id, user=user)
        except EmergencyContact.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Emergency contact not found.")
        for attr, value in validated_data.items():
            setattr(contact, attr, value)
        contact.save()
        return contact

    @staticmethod
    def delete_emergency_contact(user: UserProfile, contact_id) -> None:
        try:
            contact = EmergencyContact.objects.get(id=contact_id, user=user)
        except EmergencyContact.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Emergency contact not found.")
        contact.delete()
