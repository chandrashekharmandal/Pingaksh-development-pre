import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from utils.models import TimeStampedModel


class UserProfileManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_unusable_password()  # b-secure uses OTP, not passwords
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")
        user = self.create_user(phone_number, password, **extra_fields)
        if password:
            user.set_password(password)  # Admin can use password login
            user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Central user model. Used for regular users, guards, and admin/staff.
    Guards additionally have an associated GuardProfile (OneToOne).
    """

    ROLE_CHOICES = [
        ("USER", "Regular User"),
        ("GUARD", "Security Guard"),
        ("ADMIN", "Platform Admin"),
        ("STAFF", "Platform Staff"),
    ]

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
        ("PREFER_NOT_TO_SAY", "Prefer not to say"),
    ]

    # Core identity
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to="users/photos/", null=True, blank=True)

    # Role
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="USER")

    # Social auth identifiers
    google_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    apple_id = models.CharField(max_length=128, unique=True, null=True, blank=True)

    # Push notification token (updated on each app open)
    fcm_token = models.CharField(max_length=512, blank=True)

    # Account status
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    suspension_ends_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Django auth fields
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserProfileManager()

    class Meta:
        db_table = "users_profile"
        indexes = [
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["is_deleted", "created_at"]),
        ]

    def __str__(self):
        return f"{self.full_name or self.phone_number} [{self.role}]"

    @property
    def is_guard(self):
        return self.role == "GUARD"

    @property
    def display_name(self):
        return self.full_name or self.phone_number


class Address(TimeStampedModel):
    """Saved addresses for a user (home, office, custom). Up to 10 per user."""

    LABEL_CHOICES = [
        ("HOME", "Home"),
        ("OFFICE", "Office"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="addresses"
    )
    label = models.CharField(max_length=20, choices=LABEL_CHOICES, default="HOME")
    custom_label = models.CharField(max_length=50, blank=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default="India")
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "users_address"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "is_default"],
                condition=models.Q(is_default=True),
                name="unique_default_address_per_user",
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.label} — {self.line1}, {self.city}"


class EmergencyContact(TimeStampedModel):
    """Emergency contacts for SOS alerts. Max 5 per user."""

    RELATIONSHIP_CHOICES = [
        ("SPOUSE", "Spouse"),
        ("PARENT", "Parent"),
        ("SIBLING", "Sibling"),
        ("CHILD", "Child"),
        ("FRIEND", "Friend"),
        ("COLLEAGUE", "Colleague"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="emergency_contacts"
    )
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    relationship = models.CharField(
        max_length=20, choices=RELATIONSHIP_CHOICES, default="OTHER"
    )
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "users_emergency_contact"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "is_primary"],
                condition=models.Q(is_primary=True),
                name="unique_primary_emergency_contact",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.relationship}) for {self.user}"
