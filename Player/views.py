from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Song, Metadata
from .serializers import SongSerializer, MetadataSerializer

def rebuild_metadata():
    albums = list(Song.objects.values_list('album', flat=True).distinct())
    artists = list({artist for s in Song.objects.values_list('artists', flat=True) for artist in s})
    genres = list({g for s in Song.objects.values_list('genre', flat=True) for g in s})
    languages = list({l for s in Song.objects.values_list('language', flat=True) for l in s})
    meta, _ = Metadata.objects.get_or_create(id=Metadata.objects.first().id if Metadata.objects.exists() else None)
    meta.album = albums
    meta.artists = artists
    meta.genre = genres
    meta.language = languages
    meta.save()
    return meta

@api_view(['GET', 'POST'])
def song_list_create(request):
    if request.method == 'GET':
        songs = Song.objects.all()
        serializer = SongSerializer(songs, many=True)
        return Response(serializer.data)

    serializer = SongSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        rebuild_metadata()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def song_detail(request, pk):
    try:
        song = Song.objects.get(pk=pk)
    except Song.DoesNotExist:
        return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SongSerializer(song)
        return Response(serializer.data)

    serializer = SongSerializer(song, data=request.data)
    if request.method == 'PUT':
        if serializer.is_valid():
            serializer.save()
            rebuild_metadata()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        song.delete()
        rebuild_metadata()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def song_filter(request):
    filters = request.data.get('filter', {})
    conditions = []
    if filters.get('album'):
        for a in filters['album']:
            conditions.append(Q(album__iexact=a))
    if filters.get('artists'):
        for artist in filters['artists']:
            conditions.append(Q(artists__icontains=artist))
    if filters.get('genre'):
        for g in filters['genre']:
            conditions.append(Q(genre__icontains=g))
    if filters.get('language'):
        for l in filters['language']:
            conditions.append(Q(language__icontains=l))
    if filters.get('tags'):
        for t in filters['tags']:
            conditions.append(Q(tags__icontains=t))
    if filters.get('year'):
        for y in filters['year']:
            conditions.append(Q(year__icontains=y))
    if conditions:
        query = conditions.pop()
        for cond in conditions:
            query |= cond
        queryset = Song.objects.filter(query)
    else:
        queryset = Song.objects.all()
    serializer = SongSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def metadata_list(request):
    meta = Metadata.objects.first()
    if not meta:
        return Response({'error': 'No metadata found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = MetadataSerializer(meta)
    return Response(serializer.data)