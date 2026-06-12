from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.models import TimeStampedModel


class Review(TimeStampedModel):
    """
    Post-session rating and review.
    One review per completed booking.
    Guard's average_rating on GuardProfile is updated via signal.
    """

    booking = models.OneToOneField(
        "bookings.Booking", on_delete=models.PROTECT, related_name="review"
    )
    reviewer = models.ForeignKey(
        "users.UserProfile", on_delete=models.PROTECT, related_name="reviews_given"
    )
    guard = models.ForeignKey(
        "guards.GuardProfile", on_delete=models.PROTECT, related_name="reviews_received"
    )

    overall_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    punctuality_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    professionalism_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    communication_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    alertness_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    comment = models.TextField(blank=True, max_length=1000)

    # Moderation
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=255, blank=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        db_table = "reviews_review"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review for {self.guard} — {self.overall_rating}★"
