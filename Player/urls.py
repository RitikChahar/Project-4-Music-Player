from django.urls import path
from . import views

urlpatterns = [
    path('songs/', views.song_list_create, name='song-list-create'),
    path('songs/<uuid:pk>/', views.song_detail, name='song-detail'),
    path('filter/', views.song_filter, name='song-filter'),
    path('metadata/', views.metadata_list, name='metadata-list'),
    path('bulk_create/', views.song_bulk_create, name='song-bulk-create'),
    path('search/', views.song_search, name='song-search'),
]