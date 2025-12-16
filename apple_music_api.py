"""
Person 2: Apple music API
We access the Apple Music API and 
"""
import requests


def searched_songs(search_term, limit=10):
    url = "https://itunes.apple.com/search"

    itunes_params = { 
        'term': search_term,
        'entity': 'song', 
        'limit': limit
    }
    
    response = requests.get(url, params= itunes_params)
    data = response.json()

    songs = []
    for results in data ['results']:
        song = {
            'artist': results['artistName'],
            'title': results['trackName'],
            'artwork_url': results['artworkUrl100'],
            'preview_url': results['previewUrl']
        }  
        songs.append(song)

    return songs  

"""
Finds the preview URL for the song searched for
"""
def get_preview (artist, title):
    search = artist + " " + title
    songs = searched_songs(search, limit=1)


    if songs:
        return songs[0]['preview_url']
    return None
    

"""
Excluding the searched song, this finds shows other songs from the same artist
"""
def similar_songs(artist, title):
    songs = searched_songs(artist)
    
    # Checks length of songs
    if len(songs) == 0:
           return []
    
    result = []
    for song in songs:
        if song['title']!= title:
            result.append(song)

    return result