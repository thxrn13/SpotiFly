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
from spotify_helper import SpotifyHelper

config = configparser.ConfigParser()
config.read('.config')
PORT = config.getint('General', 'PORT')


def main(page: ft.Page):
    # Create helper instance
    spotify_helper = SpotifyHelper(page)
    logged_user = spotify_helper.logged_user
    page.on_login = spotify_helper.on_login
    page.on_logout = spotify_helper.on_logout

    page.add(
        ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                spotify_helper.login_button,
                spotify_helper.logout_button,
                logged_user,
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
                                vertical_alignment=ft.CrossAxisAlignment
                                                     .CENTER,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.SKIP_PREVIOUS,
                                        icon_color="white"
                                    ),
                                    spotify_helper.play_pause_button,
                                    ft.IconButton(
                                        icon=ft.Icons.SKIP_NEXT,
                                        icon_color="white"
                                    )
                                ],
                            ),
                        ],
                    )
                ),
            ]
        )
    )


ft.app(main, port=PORT, view=ft.WEB_BROWSER)  # type: ignore
