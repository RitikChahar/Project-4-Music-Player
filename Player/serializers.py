from rest_framework import serializers
from .models import Song, Metadata, _lower_list

class SongSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    album = serializers.CharField()
    year = serializers.IntegerField()
    artists = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    genre = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    language = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    tags = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    link = serializers.CharField(allow_blank=True)

    def validate_title(self, value):
        return value.lower()

    def validate_album(self, value):
        return value.lower()

    def validate_artists(self, value):
        return _lower_list(value)

    def validate_genre(self, value):
        return _lower_list(value)

    def validate_language(self, value):
        return _lower_list(value)

    def validate_tags(self, value):
        return _lower_list(value)

    class Meta:
        model = Song
        fields = ['id', 'title', 'album', 'year', 'artists', 'genre', 'language', 'tags', 'link']

class MetadataSerializer(serializers.ModelSerializer):
    album    = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    artists  = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    genre    = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    language = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    tags = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    year = serializers.IntegerField()

    def validate_album(self, value):
        return _lower_list(value)

    def validate_artists(self, value):
        return _lower_list(value)

    def validate_genre(self, value):
        return _lower_list(value)

    def validate_language(self, value):
        return _lower_list(value)

    def validate_tags(self, value):
        return _lower_list(value)

    class Meta:
        model = Metadata
        fields = ['id', 'album', 'artists', 'genre', 'language', 'tags', 'year']