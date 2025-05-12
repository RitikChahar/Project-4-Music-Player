# Project-4-Music-Player

A Django REST Framework service for managing song metadata, with live-updated aggregates.

## Endpoints

**List & Create Songs**  
GET /songs/ — retrieve all songs  
POST /songs/ — add a new song (skips duplicates)

**Song Detail**  
GET /songs/<uuid>/ — retrieve a single song  
PUT /songs/<uuid>/ — update a song (rebuilds metadata)  
DELETE /songs/<uuid>/ — remove a song (rebuilds metadata)

**Filter Songs**  
POST /filter/ — supply a `filter` object to query by title, album, artists, genre, language, tags or year

**Bulk Create**  
POST /bulk_create/ — import an array of songs in one request, auto-skipping existing records

**Search Titles**  
GET /search/?q=<keyword> — case-insensitive, multi-term lookup on song titles

**Metadata**  
GET /metadata/ — retrieve aggregated lists of albums, years, artists, genres, languages & tags

---

Import the Postman collection for example requests and responses:  
https://documenter.getpostman.com/view/27523601/2sB2jAbTrL  
