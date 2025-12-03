"""Person 2: Apple music API """
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
