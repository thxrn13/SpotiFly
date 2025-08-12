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

# Load environment variables from .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Read configuration from .config file
config = configparser.ConfigParser()
config.read('.config')
PORT = config.getint('General', 'PORT')
AUTH_URL = config.get('General', 'AUTH_URL')
TOKEN_URL = config.get('General', 'TOKEN_URL')
SCOPE = json.loads(config.get('General', 'SCOPE'))
USER_ENDPOINT = config.get('General', 'USER_ENDPOINT')
REDIRECT_URI = f"http://127.0.0.1:{PORT}/oauth_callback"
url = "https://github.com/mdn/webaudio-examples/blob/main/audio-basics/outfoxing.mp3?raw=true"

# Set up Security
if not os.getenv("SECRET_KEY"):
    key = Fernet.generate_key().decode()
    set_key('.env', 'SECRET_KEY', key)
else:
    key = os.getenv("SECRET_KEY")


def main(page: ft.Page):
    provider = OAuthProvider(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        authorization_endpoint=AUTH_URL,
        token_endpoint=TOKEN_URL,
        redirect_url=REDIRECT_URI,
        user_endpoint=USER_ENDPOINT,
        user_id_fn=lambda user: user.get("id"),
    )

    def get_user_info():
        if page.auth:
            headers = {
                "User-Agent": "Flet",
                "Authorization": f"Bearer {page.auth.token.access_token}"
            }
            user_resp = httpx.get(USER_ENDPOINT, headers=headers)
            user_resp.raise_for_status()
            user_info = user_resp.json()
            logged_in_user_info.value = f"Logged in as: {user_info.get('display_name', 'Unknown')}"
            page.update()

    def perform_login(e):
        saved_token = None
        ejt = page.client_storage.get("myapp.auth_token")
        if ejt:
            saved_token = decrypt(ejt, key)
        if e is not None or saved_token is not None:
            page.login(provider, saved_token=saved_token)

    def on_login(e):
        if e.error:
            raise Exception(f"Login failed: {e.error}")

        jt = page.auth.token.to_json()
        ejt = encrypt(jt, key)
        page.client_storage.set("myapp.auth_token", ejt)

        get_user_info()

    page.on_login = on_login

    def change_play_pause_button(e):
        if e.data == ft.AudioState.PAUSED.value:
            play_pause_button.icon = ft.Icons.PLAY_ARROW
            play_pause_button.on_click = lambda e: audio1.resume()
        elif e.data == ft.AudioState.PLAYING.value:
            play_pause_button.icon = ft.Icons.PAUSE
            play_pause_button.on_click = lambda e: audio1.pause()
        play_pause_button.update()

    play_pause_button = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW,
        icon_color="black",
        bgcolor="green",
        on_click=lambda _: audio1.play()
        )

    audio1 = fa.Audio(
        src=url,
        autoplay=False,
        volume=1,
        balance=0,
        on_loaded=lambda _: print("Loaded"),
        on_duration_changed=lambda e: print("Duration changed:", e.data),
        on_position_changed=lambda e: print("Position changed:", e.data),
        on_state_changed=change_play_pause_button,
        on_seek_complete=lambda _: print("Seek complete"),
    )

    page.overlay.append(audio1)

    logged_in_user_info = ft.Text()

    page.add(
        ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Button(
                    text="Authorize with Spotify",
                    on_click=lambda e: perform_login(e),
                    bgcolor="green",
                    color="white",
                    width=200,
                    height=50,
                ),
                logged_in_user_info,
                ft.BottomAppBar(
                    padding=3,
                    content=ft.Column(
                        spacing=3,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("LOREM IPSUM")
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.IconButton(icon=ft.Icons.SKIP_PREVIOUS, icon_color="white"),
                                    play_pause_button,
                                    ft.IconButton(icon=ft.Icons.SKIP_NEXT, icon_color="white")
                                ],
                            ),
                        ],
                    )
                ),
            ]
        )
    )


ft.app(main, port=PORT, view=ft.WEB_BROWSER)
