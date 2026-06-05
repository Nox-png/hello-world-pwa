from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', help_text="Referenzierender Nutzer aus dem Django User Model")
    profileImage = models.BinaryField(null=True, blank=True, help_text="Profilbild als Binärdaten")
    profileImageContentType = models.CharField(max_length=100, null=True, blank=True, help_text="MIME-Type des Profilbilds")

    def __str__(self):
        return f"Profil von {self.user.username}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def createUserProfile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
 