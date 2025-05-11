import uuid
from django.db import models
from django.db.models import JSONField

def _lower_list(values):
    return [v.lower() if isinstance(v, str) else v for v in values]

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    album = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    artists = JSONField(default=list, blank=True)
    genre = JSONField(default=list, blank=True)
    language = JSONField(default=list, blank=True)
    tags = JSONField(default=list, blank=True)
    link = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if self.title:
            self.title = self.title.lower()
        if self.album:
            self.album = self.album.lower()
        self.artists = _lower_list(self.artists)
        self.genre = _lower_list(self.genre)
        self.language = _lower_list(self.language)
        self.tags = _lower_list(self.tags)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Metadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = JSONField(default=list, blank=True)
    artists = JSONField(default=list, blank=True)
    year = models.PositiveIntegerField()
    genre = JSONField(default=list, blank=True)
    language = JSONField(default=list, blank=True)
    tags = JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        self.album = _lower_list(self.album)
        self.artists = _lower_list(self.artists)
        self.genre = _lower_list(self.genre)
        self.language = _lower_list(self.language)
        self.tags = _lower_list(self.tags)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Metadata {self.id}"
