from django.db import models

class Message(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.CharField(max_length=255, default="anonymous")
    username = models.CharField(max_length=255, default="Unknown")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_name}: {self.content[:50]}"
