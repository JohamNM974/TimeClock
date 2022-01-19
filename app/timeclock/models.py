from django.db import models
from django.contrib.auth import get_user_model

class Clock(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.CASCADE)
    clockedIn = models.DateTimeField(blank=True, null=True)
    clockedOut = models.DateTimeField(blank=True, null=True)
