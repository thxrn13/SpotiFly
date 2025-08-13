import httpx
from flet.auth import OAuthProvider


class SpotifyHelper():
    def __init__(self):
        self.headers = {}

    def create_oauth_provider(self,
                              client_id,
                              client_secret,
                              auth_url,
                              token_url,
                              redirect_url,
                              user_endpoint,
                              scopes):
        self.provider = OAuthProvider(
            client_id=client_id,
            client_secret=client_secret,
            authorization_endpoint=auth_url,
            token_endpoint=token_url,
            redirect_url=redirect_url,
            user_endpoint=user_endpoint,
            user_id_fn=lambda user: user.get("id"),
            scopes=scopes,
        )
        return self.provider

    def get_user_info(self, token):
        response = httpx.get(
            "https://api.spotify.com/v1/me",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def get_playlists(self, token, limit=50, offset=0):
        params = {
            "limit": limit,  # Adjust limit as needed
            "offset": offset,  # Start from the first page
        }
        response = httpx.get(
            "https://api.spotify.com/v1/me/playlists",
            headers=self.headers,
            params=params,
        )
        response.raise_for_status()
        playlists = response.json().get("items", [])
        useful_playlist_info = []
        for playlist in playlists:
            imgs = playlist.get("images", [{}])
            name = playlist.get("name", "Unknown Playlist")
            href = playlist.get("tracks", {}).get("href", "")
            num_tracks = playlist.get("tracks", {}).get("total", 0)
            useful_playlist_info.append({
                "name": name,
                "track_info": href,
                "num_tracks": num_tracks,
                "images": imgs
            })
        return useful_playlist_info

    def get_tracks(self, href, limit=50, offset=0):
        params = {
            "limit": limit,
            "offset": offset
        }
        response = httpx.get(
            href,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        tracks = response.json().get('items')
        useful_track_info = []
        for track in tracks:
            track_info = track.get('track')
            album = track_info.get('album')
            album_title = album.get('name')
            album_art = album.get('images')
            track_id = track_info.get('id')
            track_name = track_info.get('name')
            artists = track_info.get('artists')
            artist = ', '.join([artist_info.get('name') for artist_info in artists])
            useful_track_info.append(
                {
                    "name": track_name,
                    "album": album_title,
                    "art": album_art,
                    "id": track_id,
                    "artist": artist
                }
            )
        return useful_track_info
