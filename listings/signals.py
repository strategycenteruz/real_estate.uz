from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RealEstate
from telegram_bot.bot import send_real_estate_to_channel

@receiver(post_save, sender=RealEstate)
def post_real_estate(sender, instance, created, **kwargs):
    if created and instance.is_approved:  # faqat tasdiqlangan e’lonlar
        send_real_estate_to_channel(instance)
