import os
import flet as ft
import flet_audio as fa
from flet.auth import OAuthProvider
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

PORT = 6969
REDIRECT_URI = f"http://127.0.0.1:{PORT}/oauth_callback"
SCOPE = ["user-read-private",
         "user-read-email",
         "user-library-read",
         "user-read-recently-played",
         "user-top-read",
         "user-read-playback-state",
         "user-modify-playback-state",
         "user-read-currently-playing",
         "playlist-read-collaborative",
         "playlist-modify-public",
         "playlist-modify-private",
         "playlist-read-public",
         "playlist-read-private",
         "playlist-modify-public",
         "streaming",
         "app-remote-control",
         "user-personalized"]
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
url = "https://github.com/mdn/webaudio-examples/blob/main/audio-basics/outfoxing.mp3?raw=true"


def main(page: ft.Page):
    provider = OAuthProvider(
        client_id=CLIENT_ID,
        authorization_endpoint=AUTH_URL,
        token_endpoint=TOKEN_URL,
        redirect_url=REDIRECT_URI,
        scopes=SCOPE,
        client_secret=CLIENT_SECRET,
        user_endpoint="https://api.spotify.com/v1/me"
    )

    def login_click(e):
        page.login(provider)

    def on_login(e):
        print("Login error:", e.error)
        print("Access token:", page.auth.token)

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

    page.add(
        ft.Column(
            controls=[
                ft.Button(
                    text="Authorize with Spotify",
                    on_click=lambda e: login_click(e),
                    bgcolor="green",
                    color="white",
                    width=200,
                    height=50,
                ),
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
