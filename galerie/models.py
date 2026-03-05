from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date




class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/')
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)  # True = public / False = privé
    uploaded_at = models.DateTimeField(auto_now_add=True)
    albums = models.ManyToManyField('Album', blank=True)

    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Public' if self.is_public else 'Privé'}"

    def is_expired(self):
        """
        Renvoie True si l’image est supprimée depuis plus de 7 jours.
        """
        if self.is_deleted and self.deleted_at:
            return timezone.now() > self.deleted_at + timezone.timedelta(days=7)
        return False
    
    def days_until_permanent_delete(self):
        if self.deleted_at:
            limit = self.deleted_at + timedelta(days=30)  # 30 jours en corbeille
            remaining = (limit.date() - date.today()).days
            return max(remaining, 0)
        return None


class Album(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name