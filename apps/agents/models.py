from django.db import models
from apps.core.models import CustomUser


class Agent(models.Model):

    name        = models.CharField(max_length=200)
    name_urdu   = models.CharField(max_length=200, blank=True)
    cnic        = models.CharField(max_length=20, blank=True)
    phone       = models.CharField(max_length=50)
    address     = models.TextField(blank=True)
    city        = models.CharField(max_length=100, blank=True)
    is_deleted  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(
                    CustomUser,
                    on_delete=models.SET_NULL,
                    null=True, blank=True
                  )

    def __str__(self):
        return f"{self.name} ({self.phone})"