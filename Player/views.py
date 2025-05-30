from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Song, Metadata
from .serializers import SongSerializer, MetadataSerializer

def rebuild_metadata():
    albums = list(Song.objects.values_list('album', flat=True).distinct())
    years = list(Song.objects.values_list('year', flat=True).distinct())
    artists = list({artist for s in Song.objects.values_list('artists', flat=True) for artist in s})
    genres = list({g for s in Song.objects.values_list('genre', flat=True) for g in s})
    languages = list({l for s in Song.objects.values_list('language', flat=True) for l in s})
    tags = list({l for s in Song.objects.values_list('tags', flat=True) for l in s})
    meta, _ = Metadata.objects.get_or_create(id=Metadata.objects.first().id if Metadata.objects.exists() else None)
    meta.album = albums
    meta.artists = artists
    meta.genre = genres
    meta.language = languages
    meta.tags = tags
    meta.year = years
    meta.save()
    return meta

@api_view(['GET', 'POST'])
def song_list_create(request):
    if request.method == 'GET':
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        
        songs = Song.objects.all()
        total_songs = songs.count()
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        songs_page = songs[start_index:end_index]
        serializer = SongSerializer(songs_page, many=True)
        
        response_data = {
            'count': total_songs,
            'next': None if end_index >= total_songs else f"?page={page+1}&page_size={page_size}",
            'previous': None if page <= 1 else f"?page={page-1}&page_size={page_size}",
            'results': serializer.data
        }
        
        return Response(response_data)

    serializer = SongSerializer(data=request.data)
    if serializer.is_valid():
        title = serializer.validated_data['title']
        album = serializer.validated_data['album']
        artists = serializer.validated_data.get('artists', [])
        conditions = [Q(title__iexact=title, album__iexact=album, artists__icontains=artist)
                      for artist in artists]
        if any(Song.objects.filter(cond).exists() for cond in conditions):
            return Response(
                {"detail": "A song with that title, album and artist combination already exists."},
                status=status.HTTP_409_CONFLICT
            )
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

@api_view(['POST'])
def song_bulk_create(request):
    data = request.data
    if not isinstance(data, list):
        return Response({'detail': 'Expected a list of song objects.'}, status=status.HTTP_400_BAD_REQUEST)

    to_create = []
    for item in data:
        serializer = SongSerializer(data=item, partial=True)
        if not serializer.is_valid():
            continue
        vd = serializer.validated_data
        title = vd.get('title')
        album = vd.get('album')
        artists = vd.get('artists', []) or []
        duplicate = any(
            Song.objects.filter(
                Q(title__iexact=title),
                Q(album__iexact=album),
                artists__icontains=artist
            ).exists()
            for artist in artists
        )
        if not duplicate:
            to_create.append(item)

    if not to_create:
        return Response({'detail': 'No new songs to add.'}, status=status.HTTP_200_OK)

    serializer = SongSerializer(data=to_create, many=True, partial=True)
    if serializer.is_valid():
        songs = serializer.save()
        rebuild_metadata()
        output = SongSerializer(songs, many=True).data
        return Response(output, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def song_search(request):
    keyword = request.query_params.get('q', '')
    if not keyword:
        return Response({'detail': 'Query param "q" required.'}, status=status.HTTP_400_BAD_REQUEST)

    qs = Song.objects.filter(title__icontains=keyword.lower())
    serializer = SongSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def metadata_list(request):
    meta = Metadata.objects.first()
    if not meta:
        return Response({'error': 'No metadata found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = MetadataSerializer(meta)
    return Response(serializer.data)