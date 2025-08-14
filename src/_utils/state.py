import configparser
from dotenv import load_dotenv
import flet as ft
import os
import spotipy
from spotipy.oauth2 import SpotifyPKCE
from pathlib import Path
from _utils.views import ViewStore
from _utils.controls import ControlStore


cwd = Path(__file__).parents[2]


class AppState:
    def __init__(self, page):
        self.page = page
        self.control_store = ControlStore(self)
        self.view_store = ViewStore(self, self.control_store)

        load_dotenv()

        # Read configuration from .config file
        config = configparser.ConfigParser()
        config.read(os.path.join(cwd, 'src', 'config', '.config'))

        self.client_id = None
        self.provider = None
        self.sp = None
        # Set up Spotify API configuration
        if not os.getenv("CLIENT_ID"):
            self.get_client_id()
        else:
            self.client_id = os.getenv("CLIENT_ID")

        self.port = config.getint('GENERAL', 'PORT')
        self.redirect_url = config.get('GENERAL', 'REDIRECT_URL')
        self.scopes = config.get('GENERAL', 'SCOPES').split(",")
        if self.client_id is not None:
            self.provider = SpotifyPKCE(
                client_id=self.client_id,
                redirect_uri=self.redirect_url,
                scope=self.scopes
            )
            self.sp = spotipy.Spotify(auth_manager=self.provider)

        self.devices = {}
        self.play_state = "paused"
        self.active_device = None

        # # Initialize audio player and buttons
        # self.audio1 = fa.Audio(
        #     src="",
        #     autoplay=False,
        #     on_state_changed=self.change_play_pause_button,
        # )
        # self.page.overlay.append(self.audio1)

    def get_client_id(self):
        self.page.go('/client_id_form')

    def save_client_id(self, e):
        os.environ["CLIENT_ID"] = str(self.control_store.client_id_input_field.value)
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
        self.control_store.logged_user.visible = True
        self.control_store.logged_user.value = f"Current User: {results['display_name']}"
        self.page.update()

    def on_login(self, e):
        self.get_user_info()
        self.show_playlists()
        self.get_user_devices()
        self.change_play_pause_button()
        self.toggle_login_button()

    def change_play_pause_button(self):
        if self.play_state == "paused":
            self.control_store.play_pause_button.icon = ft.Icons.PLAY_ARROW
        elif self.play_state == "playing":
            self.control_store.play_pause_button.icon = ft.Icons.PAUSE
        self.page.update()

    def logout_button_click(self, e):
        self.on_logout(e)

    def on_logout(self, e):
        os.remove(os.path.join(cwd, '.cache'))
        self.toggle_login_button()
        self.control_store.playlists_view.visible = False
        self.control_store.playlists_view.controls.clear()
        self.control_store.tracks_view.visible = False
        self.control_store.tracks_view.controls.clear()
        self.control_store.logged_user.visible = False
        self.page.update()

    def toggle_login_button(self):
        if self.control_store.login_button.visible:
            self.control_store.login_button.visible = False
            self.control_store.logout_button.visible = True
        else:
            self.control_store.login_button.visible = True
            self.control_store.logout_button.visible = False
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
        self.control_store.playlists_view.visible = True
        self.control_store.playlists_view.controls.clear()
        playlists = self.get_playlists()
        print(f"Playlists fetched: {len(playlists)}")
        self.control_store.playlists_view.controls.append(
            ft.Text("Your Playlists", size=20, weight=ft.FontWeight.BOLD)
        )
        for playlist in playlists:
            self.control_store.playlists_view.controls.append(
                self.control_store.create_playlist_card(playlist)
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
        self.control_store.tracks_view.visible = True
        self.control_store.tracks_view.controls.clear()
        tracks = self.get_tracks(playlist)
        print(f"Tracks fetched: {len(tracks)}")
        self.control_store.tracks_view.controls.append(
            ft.Text(f"{playlist['name']}", size=20, weight=ft.FontWeight.BOLD)
        )
        for track in tracks:
            self.control_store.tracks_view.controls.append(
                self.control_store.create_track_card(track)
            )
        self.page.update()

    def get_user_devices(self):
        response = self.sp.devices()
        devices = response.get('devices')
        for device in devices:
            self.control_store.device_list.options.append(
                self.control_store.create_device_option(device)
            )

    def connect_to_device(self, device_name):
        device_data = self.devices[device_name]
        remain_playing = True
        if self.play_state == 'paused':
            remain_playing = False
        self.sp.transfer_playback(device_data.get('id'), force_play=remain_playing)
        self.change_play_pause_button()
        self.active_device = device_data.get('id')
        self.get_currently_playing()

    def play_pause(self):
        response = self.sp.current_playback()
        if response.get('is_playing'):
            self.play_state = 'paused'
            self.sp.pause_playback(self.active_device)
        else:
            self.play_state = 'playing'
            self.sp.start_playback(self.active_device)
        self.change_play_pause_button()

    def get_currently_playing(self):
        response = self.sp.current_playback()
        track_title = response.get('item').get('name')
        artists = ', '.join([artist.get('name') for artist in response.get('item').get('artists')])
        
    def play_track(self, id):
        pass
