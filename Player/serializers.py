from rest_framework import serializers
from .models import Song, Metadata

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'title', 'album', 'artists', 'genre', 'language']

class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        fields = ['id', 'album', 'artists', 'genre', 'language']