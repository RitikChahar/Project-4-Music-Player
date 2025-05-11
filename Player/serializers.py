from rest_framework import serializers
from .models import Song, Metadata, _lower_list

class SongSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_null=True, default=None)
    album = serializers.CharField(required=False, allow_null=True, default=None)
    year = serializers.IntegerField(required=False, allow_null=True, default=None)
    artists = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False, allow_null=True, default=None)
    genre = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False, allow_null=True, default=None)
    language = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False, allow_null=True, default=None)
    tags = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False, allow_null=True, default=None)
    link = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)

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
    year = serializers.ListField(child=serializers.CharField(), allow_empty=True)

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