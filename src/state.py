import os
import spotipy
import flet as ft
from spotipy.oauth2 import SpotifyPKCE
from dotenv import load_dotenv
import configparser
from pathlib import Path
cwd = Path(__file__).parents[1]


class AppState:
    def __init__(self, page):
        self.page = page

        load_dotenv()

        # Read configuration from .config file
        config = configparser.ConfigParser()
        config.read('.config')

        self.client_id = None
        self.provider = None
        self.sp = None
        # Set up Spotify API configuration
        if not os.getenv("CLIENT_ID"):
            self.get_client_id()
        else:
            self.client_id = os.getenv("CLIENT_ID")

        self.port = config.getint('General', 'PORT')
        self.redirect_url = config.get('General', 'REDIRECT_URL')
        self.scopes = config.get('General', 'SCOPES').split(",")
        if self.client_id:
            self.provider = SpotifyPKCE(
                client_id=self.client_id,
                redirect_uri=self.redirect_url,
                scope=self.scopes
            )
            self.sp = spotipy.Spotify(auth_manager=self.provider)
        self.logged_user = ft.Text(visible=False)

        # # Initialize audio player and buttons
        # self.audio1 = fa.Audio(
        #     src="",
        #     autoplay=False,
        #     on_state_changed=self.change_play_pause_button,
        # )
        # self.page.overlay.append(self.audio1)

        self.clear_client_id_button = ft.ElevatedButton(
            text="Delete Client ID",
            bgcolor="red",
            color="black",
            on_click=lambda e: self.delete_client_id(e),
            visible=True
        )

        self.play_pause_button = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            icon_color="black",
            bgcolor="green",
            on_click=None,
            icon_size=20,
        )

        self.login_button = ft.ElevatedButton(
            text="Login with Spotify",
            on_click=lambda e: self.perform_login(e),
            bgcolor="green",
            color="white",
            width=150,
            height=25
        )

        self.logout_button = ft.ElevatedButton(
            text="Logout",
            on_click=lambda e: self.logout_button_click(e),
            bgcolor="red",
            color="white",
            width=100,
            height=25,
            visible=False,
        )

        self.playlists_view = ft.ListView(
            visible=False,
            spacing=10,
            padding=10,
            controls=[],
            width=400,
            expand=True,
        )

        self.tracks_view = ft.ListView(
            visible=False,
            spacing=10,
            padding=10,
            controls=[],
            width=400,
            expand=True,
        )

        self.client_id_input_field = ft.TextField(
                                    hint_text="Paste your Client ID Here",
                                )
        self.client_id_submit_button = ft.ElevatedButton(
                    text="Submit",
                    bgcolor="green",
                    color="black",
                    on_click=lambda e: self.save_client_id(e),
                    )

    def get_client_id(self):
        self.page.go('/client_id_form')

    def save_client_id(self, e):
        os.environ["CLIENT_ID"] = str(self.client_id_input_field.value)
        with open(os.path.join(cwd, '.env'), 'x') as f:
            f.write(f"CLIENT_ID = {os.getenv("CLIENT_ID")}")
        self.client_id = os.getenv("CLIENT_ID")
        self.page.go('/')
        self.provider = SpotifyPKCE(
                            client_id=self.client_id,
                            redirect_uri=self.redirect_url,
                            scope=self.scopes
                        )
        self.sp = spotipy.Spotify(auth_manager=self.provider)

    def delete_client_id(self, e):
        os.environ.pop("CLIENT_ID")
        os.remove(os.path.join(cwd, '.env'))

    def check_logged_in(self):
        if self.provider:
            self.on_login(None)

    def perform_login(self, e):
        self.provider.get_access_token()
        self.on_login(e)

    def get_user_info(self):
        results = self.sp.current_user()
        self.logged_user.visible = True
        self.logged_user.value = f"Current User: {results['display_name']}"
        self.page.update()

    def on_login(self, e):
        self.get_user_info()
        self.show_playlists()
        self.toggle_login_button()

    def change_play_pause_button(self, e):
        if e.data == ft.AudioState.PAUSED.value:
            self.play_pause_button.icon = ft.Icons.PLAY_ARROW
            self.play_pause_button.on_click = None
        elif e.data == ft.AudioState.PLAYING.value:
            self.play_pause_button.icon = ft.Icons.PAUSE
            self.play_pause_button.on_click = None
        self.page.update()

    def logout_button_click(self, e):
        self.on_logout(e)

    def on_logout(self, e):
        os.remove(os.path.join(cwd, '.cache'))
        self.toggle_login_button()
        self.playlists_view.visible = False
        self.playlists_view.controls.clear()
        self.tracks_view.visible = False
        self.tracks_view.controls.clear()
        self.logged_user.visible = False
        self.page.update()

    def toggle_login_button(self):
        if self.login_button.visible:
            self.login_button.visible = False
            self.logout_button.visible = True
        else:
            self.login_button.visible = True
            self.logout_button.visible = False
        self.page.update()

    def get_playlists(self, offset=0, limit=50):
        playlists_response = self.sp.current_user_playlists()
        playlists = playlists_response.get('items')
        useful_playlist_info = []
        for playlist in playlists:
            imgs = playlist.get("images", [{}])
            name = playlist.get("name", "Unknown Playlist")
            id = playlist.get("id")
            num_tracks = playlist.get("tracks", {}).get("total", 0)
            useful_playlist_info.append({
                "name": name,
                "id": id,
                "num_tracks": num_tracks,
                "images": imgs
            })
        return useful_playlist_info

    def show_playlists(self):
        print("Showing playlists")
        self.playlists_view.visible = True
        self.playlists_view.controls.clear()
        playlists = self.get_playlists()
        print(f"Playlists fetched: {len(playlists)}")
        self.playlists_view.controls.append(
            ft.Text("Your Playlists", size=20, weight=ft.FontWeight.BOLD)
        )
        for playlist in playlists:
            self.playlists_view.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        leading=ft.Image(
                            src=playlist["images"][0].get("url", ""),
                            width=30,
                            height=30,
                            fit=ft.ImageFit.COVER
                        ),
                        title=ft.Text(playlist["name"]),
                        subtitle=ft.Text(f"{playlist['num_tracks']} tracks"),
                        data=playlist,
                        on_click=lambda e: self.show_tracks(e.control.data)
                    ),
                )
            )
        self.page.update()

    def get_tracks(self, playlist):
        num_tracks = playlist['num_tracks']
        batches = num_tracks // 100
        extras = num_tracks % 100
        tracks = []
        playlist_id = playlist['id']
        for i in range(0, batches):
            batch = self.get_batched_tracks(index=i, playlist_id=playlist_id).get('items')
            for track in batch:
                tracks.append(self.format_track_info(track))
        if extras > 0:
            final_batch = self.get_batched_tracks(index=batches, playlist_id=playlist_id).get('items')
            for track in final_batch:
                tracks.append(self.format_track_info(track))
        return tracks

    def get_batched_tracks(self, index, playlist_id):
        return self.sp.playlist_items(
                fields='items(track(name, id, artists(name), album(images, !name, !artists)))',
                playlist_id=playlist_id,
                offset=index*100,
                limit=100,
                additional_types=("track")
                )

    def format_track_info(self, track):
        track = track.get('track')
        return {
                "art": track.get('album').get('images'),
                "name": track.get('name'),
                "artist": ', '.join([artist.get('name')
                                     for artist in track.get('artists')]),
                "id": track.get('id')
                }

    def show_tracks(self, playlist):
        print(f"Showing tracks for playlist: {playlist['name']}")
        self.tracks_view.visible = True
        self.tracks_view.controls.clear()
        tracks = self.get_tracks(playlist)
        print(f"Tracks fetched: {len(tracks)}")
        self.tracks_view.controls.append(
            ft.Text(f"{playlist['name']}", size=20, weight=ft.FontWeight.BOLD)
        )
        for track in tracks:
            self.tracks_view.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        leading=ft.Image(
                            src=track.get('art', [{}])[0].get('url', ''),
                            width=30,
                            height=30,
                            fit=ft.ImageFit.COVER
                        ),
                        title=ft.Text(track.get("name", "Unknown Track")),
                        subtitle=ft.Text(track.get('artist', 'Unknown Artist')),
                        on_click=self.play_track(track['id'])
                    ),
                )
            )
        self.page.update()

    def play_track(self, id):
        pass
