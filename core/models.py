# core/models.py

from django.db import models

class UserSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    session_string = models.TextField(null=True, blank=True)  # Store Telethon session string
    is_logged_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_id
