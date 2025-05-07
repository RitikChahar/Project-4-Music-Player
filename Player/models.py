import uuid
from django.db import models
from django.db.models import JSONField

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    album = models.CharField(max_length=255)
    artists = JSONField(default=list, blank=True)
    genre = JSONField(default=list, blank=True)
    language = JSONField(default=list, blank=True)

    def __str__(self):
        return self.title

class Metadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = JSONField(default=list, blank=True)
    artists = JSONField(default=list, blank=True)
    genre = JSONField(default=list, blank=True)
    language = JSONField(default=list, blank=True)

    def __str__(self):
        return f"Metadata {self.id}"