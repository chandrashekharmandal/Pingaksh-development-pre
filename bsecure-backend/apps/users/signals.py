from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_wallet_and_preferences(sender, instance, created, **kwargs):
    """
    Auto-create a Wallet and NotificationPreference for every new user.
    This is done via signal so it happens regardless of how the user is created.
    """
    if not created:
        return

    # Avoid circular import — import inside signal
    from apps.payments.models import Wallet
    from apps.notifications.models import NotificationPreference

    Wallet.objects.get_or_create(user=instance)
    NotificationPreference.objects.get_or_create(user=instance)
