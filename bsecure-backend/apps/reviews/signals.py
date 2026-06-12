from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review


@receiver(post_save, sender=Review)
def update_guard_average_rating(sender, instance, created, **kwargs):
    """Recalculate guard's average rating whenever a review is saved."""
    if not created:
        return

    guard = instance.guard
    reviews = Review.objects.filter(guard=guard, is_hidden=False)
    total = reviews.count()

    if total == 0:
        guard.average_rating = 0.00
        guard.total_reviews = 0
    else:
        avg = reviews.aggregate(
            avg=__import__("django.db.models", fromlist=["Avg"]).Avg("overall_rating")
        )["avg"]
        guard.average_rating = round(avg, 2)
        guard.total_reviews = total

    guard.save(update_fields=["average_rating", "total_reviews"])
