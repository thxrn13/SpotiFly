import os
import json
import httpx
import flet as ft
import flet_audio as fa
from cryptography.fernet import Fernet
from flet.auth import OAuthProvider
from flet.security import encrypt, decrypt
from dotenv import load_dotenv, set_key
import configparser


class SpotifyHelper():
    def __init__(self, page: ft.Page):
        self.page = page
        # Load environment variables from .env
        load_dotenv()

        # Read configuration from .config file
        config = configparser.ConfigParser()
        config.read('.config')

        # Set up Spotify API configuration
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.port = config.getint('General', 'PORT')
        self.auth_url = config.get('General', 'AUTH_URL')
        self.token_url = config.get('General', 'TOKEN_URL')
        self.user_endpoint = config.get('General', 'USER_ENDPOINT')
        self.redirect_url = f"http://127.0.0.1:{self.port}/oauth_callback"
        self.scopes = [
            "playlist-read-private",
            "playlist-read-collaborative",
            "user-read-private",
            "user-read-email"]

        # Initialize variables
        self.saved_token = None
        self.provider = self.create_oauth_provider()
        self.key = None
        self.logged_user = ft.Text()
        self.headers = None

        # Set up Security
        if not os.getenv("SECRET_KEY"):
            self.key = Fernet.generate_key().decode()
            set_key('.env', 'SECRET_KEY', self.key)
        else:
            self.key = os.getenv("SECRET_KEY")

        # Initialize audio player and buttons
        self.audio1 = fa.Audio(
            src="https://github.com/rafaelreis-hotmart/Audio-Sample-files/raw/master/sample.mp3",
            autoplay=False,
            on_state_changed=self.change_play_pause_button,
        )
        self.page.overlay.append(self.audio1)

        self.play_pause_button = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            icon_color="black",
            bgcolor="green",
            on_click=lambda _: self.audio1.play(),
            icon_size=20,
        )

        self.login_button = ft.ElevatedButton(
            text="Login with Spotify",
            on_click=lambda e: self.perform_login(e),
            bgcolor="green",
            color="white",
            width=150,
            height=25,
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

    def create_oauth_provider(self):
        self.provider = OAuthProvider(
            client_id=self.client_id,  # type: ignore
            client_secret=self.client_secret,  # type: ignore
            authorization_endpoint=self.auth_url,
            token_endpoint=self.token_url,
            redirect_url=self.redirect_url,
            user_endpoint=self.user_endpoint,
            user_id_fn=lambda user: user.get("id"),
            scopes=self.scopes,
        )
        return self.provider

    def get_user_info(self):
        if self.page.auth:
            user_resp = httpx.get(self.user_endpoint, headers=self.headers)
            user_resp.raise_for_status()
            user_info = user_resp.json()
            self.logged_user.value = f"Logged in as: {
                user_info.get('display_name', 'Unknown')}"
            self.page.update()

    def perform_login(self, e):
        self.saved_token = None
        ejt = self.page.client_storage.get("myapp.auth_token")
        if ejt:
            self.saved_token = decrypt(ejt, self.key)  # type: ignore
        if e is not None or self.saved_token is not None:
            self.page.login(self.provider, saved_token=self.saved_token)  # type: ignore

    def on_login(self, e):
        if e.error:
            raise Exception(f"Login failed: {e.error}")

        jt = self.page.auth.token.to_json()  # type: ignore
        ejt = encrypt(jt, self.key)  # type: ignore
        self.page.client_storage.set("myapp.auth_token", ejt)
        self.headers = {
                    "User-Agent": "Flet",
                    "Authorization":
                    f"Bearer {self.page.auth.token.access_token}"  # type: ignore
                    }
        self.get_user_info()
        self.show_playlists()
        self.toggle_login_button()

    def change_play_pause_button(self, e):
        if e.data == ft.AudioState.PAUSED.value:
            self.play_pause_button.icon = ft.Icons.PLAY_ARROW
            self.play_pause_button.on_click = lambda e: self.audio1.resume()
        elif e.data == ft.AudioState.PLAYING.value:
            self.play_pause_button.icon = ft.Icons.PAUSE
            self.play_pause_button.on_click = lambda e: self.audio1.pause()
        self.page.update()

    def logout_button_click(self, e):
        self.page.client_storage.remove("myapp.auth_token")
        self.page.logout()

    def on_logout(self, e):
        self.toggle_login_button()
        self.playlists_view.visible = False
        self.playlists_view.controls.clear()
        self.page.update()

    def toggle_login_button(self):
        self.login_button.visible = self.page.auth is None
        self.logged_user.visible = self.logout_button.visible = self.page.auth is not None
        self.page.update()

    def get_playlists(self, offset=0, limit=50):
        if not self.page.auth:
            return []
        params = {
            "limit": limit,
            "offset": offset
        }
        # Fetch playlists from Spotify API
        playlists_resp = httpx.get(
            "https://api.spotify.com/v1/me/playlists",
            headers=self.headers,
            params=params
        )
        playlists_resp.raise_for_status()
        playlists = playlists_resp.json().get("items", [])
        useful_playlist_info = []
        for playlist in playlists:
            imgs = playlist.get("images", [{}])
            name = playlist.get("name", "Unknown Playlist")
            href = playlist.get("tracks", {}).get("href", "")
            num_tracks = playlist.get("tracks", {}).get("total", 0)
            useful_playlist_info.append({
                "name": name,
                "href": href,
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
                    ),
                )
            )
        self.page.update()
