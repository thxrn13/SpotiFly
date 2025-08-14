import flet as ft


class ControlStore:
    def __init__(self, app_state):
        self.app_state = app_state

        self.clear_client_id_button = ft.ElevatedButton(
            text="Delete Client ID",
            bgcolor="red",
            color="black",
            on_click=lambda e: self.app_state.delete_client_id(e),
            visible=True
        )

        self.play_pause_button = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            icon_color="black",
            bgcolor="green",
            on_click=None,
            icon_size=20,
        )

        self.logged_user = ft.Text(visible=False)

        self.login_button = ft.ElevatedButton(
            text="Login with Spotify",
            on_click=lambda e: self.app_state.perform_login(e),
            bgcolor="green",
            color="white",
            width=150,
            height=25
        )

        self.logout_button = ft.ElevatedButton(
            text="Logout",
            on_click=lambda e: self.app_state.logout_button_click(e),
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
                    on_click=lambda e: self.app_state.save_client_id(e),
                    )

        self.app_bar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                icon_color="white",
                on_click=lambda _: app_state.page.go("/"),
            ),
            title=ft.Text("SpotiFly"),
            center_title=True,
            bgcolor="black",
            actions=[
                self.logout_button,
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color="white",
                    on_click=lambda _: app_state.page.go("/settings"),
                ),
            ]
        )

        self.bottom_app_bar = ft.BottomAppBar(
                                        padding=5,
                                        content=ft.Column(
                                            spacing=5,
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
                                                        self.play_pause_button,
                                                        ft.IconButton(
                                                            icon=ft.Icons.SKIP_NEXT,
                                                            icon_color="white"
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    )

    def create_track_card(self, track):
        track_card = ft.Card(
                        content=ft.ListTile(
                            leading=ft.Image(
                                src=track.get('art', [{}])[0].get('url', ''),
                                width=30,
                                height=30,
                                fit=ft.ImageFit.COVER
                            ),
                            title=ft.Text(track.get("name", "Unknown Track")),
                            subtitle=ft.Text(track.get('artist', 'Unknown Artist')),
                            on_click=self.app_state.play_track(track['id'])
                        ),
                    )
        return track_card

    def create_playlist_card(self, playlist):
        return ft.Card(
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
                        on_click=lambda e: self.app_state.show_tracks(e.control.data)
                    ),
                )
